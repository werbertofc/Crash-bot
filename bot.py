import telebot
import subprocess

API_TOKEN = '7972626459:AAGjV9QjaDRfEYXOO-X4TgXoWo2MqQbwMz8'  # Substitua pelo seu API Token
bot = telebot.TeleBot(API_TOKEN)

# Lista de IDs autorizados
AUTHORIZED_USERS = [6430703027]  # Substitua pelo seu ID

# Função para verificar se o usuário está autorizado
def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Olá, tudo bem? Seja bem-vindo ao bot!\n\n"
        "Aqui estão os comandos disponíveis:\n"
        "/crash <IP:PORT> <porta> <duração> - Executa um ataque no IP especificado.\n"
        "/adduser <ID> - Adiciona um novo usuário à lista de autorizados.\n"
        "/removeuser <ID> - Remove um usuário da lista de autorizados.\n"
        "/meuid - Mostra o seu ID de usuário.\n\n"
        "Apenas usuários autorizados podem executar comandos especiais como adicionar e remover usuários."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['adduser'])
def add_user(message):
    if message.from_user.id not in AUTHORIZED_USERS:
        bot.reply_to(message, "Você não tem permissão para adicionar usuários.")
        return

    try:
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message, "Uso correto: /adduser <ID>")
            return

        new_user_id = int(command_parts[1])
        if new_user_id in AUTHORIZED_USERS:
            bot.reply_to(message, f"O ID {new_user_id} já está autorizado.")
        else:
            AUTHORIZED_USERS.append(new_user_id)
            bot.reply_to(message, f"O ID {new_user_id} foi adicionado à lista de usuários autorizados.")
    except ValueError:
        bot.reply_to(message, "Por favor, forneça um ID válido.")
    except Exception as e:
        bot.reply_to(message, f"Ocorreu um erro: {str(e)}")

@bot.message_handler(commands=['removeuser'])
def remove_user(message):
    if message.from_user.id not in AUTHORIZED_USERS:
        bot.reply_to(message, "Você não tem permissão para remover usuários.")
        return

    try:
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message, "Uso correto: /removeuser <ID>")
            return

        remove_user_id = int(command_parts[1])
        if remove_user_id not in AUTHORIZED_USERS:
            bot.reply_to(message, f"O ID {remove_user_id} não está na lista de autorizados.")
        else:
            AUTHORIZED_USERS.remove(remove_user_id)
            bot.reply_to(message, f"O ID {remove_user_id} foi removido da lista de usuários autorizados.")
    except ValueError:
        bot.reply_to(message, "Por favor, forneça um ID válido.")
    except Exception as e:
        bot.reply_to(message, f"Ocorreu um erro: {str(e)}")

@bot.message_handler(commands=['crash'])
def crash_server(message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, "Você não tem permissão para executar este comando.")
        return

    try:
        command_parts = message.text.split()
        if len(command_parts) == 4:
            ip_port = command_parts[1]
            port = command_parts[2]  # Porta
            duration = command_parts[3]  # Duração (em segundos)

            if ':' not in ip_port:
                bot.reply_to(message, "Formato inválido de IP e porta. Use o formato: IP:PORT")
                return

            ip, _ = ip_port.split(':')  # Ignora a porta no IP e pega apenas o IP

            # Apenas responde com a mensagem de sucesso
            bot.reply_to(message, f"Comando de ataque enviado para {ip_port}!")

        else:
            bot.reply_to(message, "Comando inválido. Use o formato: /crash <IP:PORT> <porta> <duração>")
    except ValueError:
        bot.reply_to(message, "Por favor, forneça valores válidos.")
    except Exception as e:
        bot.reply_to(message, f"Ocorreu um erro: {str(e)}")

@bot.message_handler(commands=['meuid'])
def send_user_id(message):
    try:
        user_id = message.from_user.id
        bot.reply_to(message, f"Seu ID de usuário é: {user_id}")
    except Exception as e:
        bot.reply_to(message, f"Ocorreu um erro ao obter seu ID: {str(e)}")

# Iniciar o bot
bot.polling()