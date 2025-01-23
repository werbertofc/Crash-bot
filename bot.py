import os
import subprocess
import requests  # Para lidar com a API de likes
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
        "/crash <IP:PORT> <porta> <duração> - Envia um ataque ao IP especificado.\n"
        "/like <UID> - Envia 100 likes para o jogador com o UID especificado.\n"
        "/meuid - Mostra seu ID de usuário.\n\n"
        "Comandos para VIPs e dono:\n"
        "/adduser <ID> - Adiciona um usuário autorizado.\n"
        "/removeuser <ID> - Remove um usuário autorizado.\n"
        "/promovervip <ID> - Promove um usuário a VIP.\n"
        "/rebaixarvip <ID> - Remove a status de VIP de um usuário.\n\n"
        "Comandos exclusivos do dono:\n"
        "/addcomandovip <comando> - Restringe o comando para VIPs.\n"
        "/revcomandovip <comando> - Remove a restrição de comando VIP.\n"
        "/listusers - Mostra a lista de usuários registrados e seus cargos."
    )
    bot.send_message(message.chat.id, welcome_text)

# Comando /like
@bot.message_handler(commands=['like'])
def send_likes(message):
    try:
        # Divide a mensagem em partes
        command_parts = message.text.split()
        
        # Verifica se o UID foi enviado
        if len(command_parts) != 2:
            bot.send_message(message.chat.id, "Uso correto: /like <UID>")
            return
        
        # Extrai o UID
        uid = command_parts[1]
        
        # Define a URL da API com 100 likes como padrão
        url = f"https://api.nowgarena.com/api/send_likes?uid={uid}&key=projetoswq"
        
        # Envia a solicitação para a API
        response = requests.get(url)
        data = response.json()  # Analisa a resposta JSON
        
        # Verifica se a API respondeu com sucesso
        if data.get("success"):
            likes_info = data.get("Likes_Info", {})
            name = likes_info.get("Name", "Desconhecido")
            level = likes_info.get("Level", "Desconhecido")
            region = likes_info.get("Region", "Desconhecida")
            likes_before = likes_info.get("Likes before", "N/A")
            likes_after = likes_info.get("Likes later", "N/A")
            bot_send = likes_info.get("Bot_Send", "N/A")
            speed = likes_info.get("Speed", "N/A")
            
            # Envia os detalhes no Telegram
            bot.send_message(
                message.chat.id,
                (
                    f"✅ Likes enviados com sucesso!\n\n"
                    f"👤 Nome: {name}\n"
                    f"🏅 Nível: {level}\n"
                    f"🌍 Região: {region}\n"
                    f"👍 Likes antes: {likes_before}\n"
                    f"✅ Likes depois: {likes_after}\n"
                    f"🚀 Likes enviados: {bot_send}\n"
                    f"⚡ Velocidade: {speed}"
                )
            )
        else:
            bot.send_message(message.chat.id, "❌ Ocorreu um erro ao enviar os likes. Tente novamente mais tarde.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Erro: {str(e)}")

# Demais comandos (como /crash, /meuid, etc.) permanecem iguais
# ... [Insira o restante do código fornecido por você aqui] ...

# Inicia o bot
bot.polling()