import os
import subprocess
import telebot
import requests
from threading import Thread

# Token e ID do dono
BOT_TOKEN = '7972626459:AAGjV9QjaDRfEYXOO-X4TgXoWo2MqQbwMz8'
OWNER_ID = 6430703027

# Inicialização do bot
bot = telebot.TeleBot(BOT_TOKEN)

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


# Comando /likes (atualizado)
@bot.message_handler(commands=['likes'])
def send_likes(message):
    msg_split = message.text.split()
    if len(msg_split) < 2:
        bot.send_message(message.chat.id, "❌ Uso correto: /likes <ID>")
        return

    player_id = msg_split[1]
    default_quantity = 100

    bot.send_message(message.chat.id, f"✨ Enviando {default_quantity} likes para o jogador {player_id}. Aguarde...")

    def process_likes():
        api_url = f"https://api.nowgarena.com/api/send_likes?uid={player_id}&quantity={default_quantity}&key=projetoswq"
        try:
            response = requests.get(api_url)
            data = response.json()

            if data.get("success"):
                bot.send_message(
                    message.chat.id,
                    f"✅ {default_quantity} likes enviados com sucesso para o jogador {player_id}!",
                    parse_mode="Markdown"
                )
            else:
                bot.send_message(
                    message.chat.id,
                    "❌ Não foi possível enviar likes. Tente novamente mais tarde.",
                    parse_mode="Markdown"
                )
        except Exception:
            bot.send_message(
                message.chat.id,
                "❌ Erro ao processar a solicitação. Tente novamente mais tarde.",
                parse_mode="Markdown"
            )

    # Executa em uma nova thread
    Thread(target=process_likes).start()


# Comando /checkban (atualizado)
@bot.message_handler(commands=['checkban'])
def check_ban(message):
    msg_split = message.text.split()
    if len(msg_split) < 2:
        bot.send_message(message.chat.id, "❌ Uso correto: /checkban <ID do jogador>")
        return

    player_id = msg_split[1]
    bot.send_message(message.chat.id, "🔍 *Analisando a conta, por favor aguarde...*", parse_mode="Markdown")

    def process_checkban():
        api_url = f"https://api.nowgarena.com/api/check_banned?uid={player_id}"
        try:
            response = requests.get(api_url)
            data = response.json()

            if data.get("status") == "success":
                is_banned = data.get("isBanned")
                if is_banned == "no":
                    bot.send_message(
                        message.chat.id,
                        f"✅ *A conta não está banida!*\n\n🆔 ID: {data.get('uid')}",
                        parse_mode="Markdown"
                    )
                elif is_banned == "yes":
                    period = data.get("period", "indefinido")
                    bot.send_message(
                        message.chat.id,
                        f"🚫 *A conta está banida!*\n\n🆔 ID: {data.get('uid')}\n⏳ Período: {period} dias",
                        parse_mode="Markdown"
                    )
                else:
                    bot.send_message(message.chat.id, "❌ *Erro ao verificar a conta. Tente novamente mais tarde.*", parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "❌ *Erro ao processar a solicitação. Tente novamente mais tarde.*", parse_mode="Markdown")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ *Erro ao processar a solicitação: {str(e)}*", parse_mode="Markdown")

    # Executa em uma nova thread
    Thread(target=process_checkban).start()


# Comando /start (revisado)
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
        "/likes <ID> - Envia 100 likes para o jogador 👍\n"
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


# Inicia o bot
if __name__ == "__main__":
    bot.polling(none_stop=True)