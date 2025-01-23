import telebot
import requests
from threading import Thread

API_TOKEN = "SEU_API_TOKEN_AQUI"  # Substitua pelo token do seu bot
bot = telebot.TeleBot(API_TOKEN)

# Comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_message = (
        "👋 Bem-vindo ao Bot!\n\n"
        "📋 *Comandos disponíveis:*\n"
        "  - /info <ID> ➡️ Mostra informações do jogador\n"
        "  - /likes <ID> <QUANTIDADE> ➡️ Envia likes para o jogador\n"
        "  - /checkban <ID> ➡️ Verifica se a conta está banida\n"
        "  - /comprarbot ➡️ Informações para comprar o bot\n\n"
        "Qualquer dúvida, entre em contato: [t.me/werbert_ofc](https://t.me/werbert_ofc)"
    )
    bot.send_message(message.chat.id, welcome_message, parse_mode="Markdown")

# Comando /info
@bot.message_handler(commands=['info'])
def player_info(message):
    msg_split = message.text.split()
    if len(msg_split) < 2:
        bot.send_message(message.chat.id, "❌ Uso correto: /info <ID do jogador>")
        return

    player_id = msg_split[1]
    bot.send_message(message.chat.id, "🔍 *Buscando informações da conta, por favor aguarde...*", parse_mode="Markdown")

    def process_info():
        api_url = f"https://api.nowgarena.com/api/player_info?uid={player_id}&key=projetoswq"
        try:
            response = requests.get(api_url)
            data = response.json()

            if data.get("success"):
                player_info = data["data"]["PlayerBasicInfo"]
                guild_info = data["data"].get("GuildInfo", {})
                pet_info = data["data"].get("PetInfo", {})
                social_info = data["data"].get("SocialInfo", {})

                info_message = (
                    f"🎮 *Informações do Jogador*\n"
                    f"👤 *Nickname:* {player_info['AccountNickname']}\n"
                    f"🌎 *Região:* {player_info['AccountRegion']}\n"
                    f"🔢 *Nível:* {player_info['AccountLevel']}\n"
                    f"⭐ *Likes:* {player_info['PlayerLikes']}\n"
                    f"📅 *Último login:* {player_info['Last_Login_At']}\n\n"
                    
                    f"🛡️ *Rank BR:* {player_info['BRRank']['Rank']} (Máx: {player_info['BRRank']['MaxRank']})\n"
                    f"⚔️ *Rank CS:* {player_info['CSRank']['Rank']} (Máx: {player_info['CSRank']['MaxRank']})\n"
                    
                    f"🏠 *Guilda:* {guild_info.get('GuildName', 'Sem guilda')}\n"
                    f"🐾 *Pet:* {pet_info.get('name', 'Nenhum pet equipado')}\n"
                    
                    f"📋 *Assinatura:* {social_info.get('AccountSignature', 'Nenhuma assinatura')}"
                )
                bot.send_message(message.chat.id, info_message, parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "❌ *Erro ao buscar informações. Tente novamente mais tarde.*", parse_mode="Markdown")
        except Exception:
            bot.send_message(message.chat.id, "❌ *Erro ao processar a solicitação. Tente novamente mais tarde.*", parse_mode="Markdown")

    Thread(target=process_info).start()

# Comando /likes
@bot.message_handler(commands=['likes'])
def send_likes(message):
    msg_split = message.text.split()
    if len(msg_split) < 3:
        bot.send_message(message.chat.id, "❌ Uso correto: /likes <ID do jogador> <QUANTIDADE>")
        return

    player_id = msg_split[1]
    likes_quantity = msg_split[2]
    bot.send_message(message.chat.id, "👍 *Enviando likes, aguarde...*", parse_mode="Markdown")

    def process_likes():
        api_url = f"https://api.nowgarena.com/api/send_likes?uid={player_id}&key=projetoswq"
        try:
            response = requests.get(api_url)
            data = response.json()

            if data.get("success"):
                bot.send_message(message.chat.id, f"✅ *Likes enviados com sucesso!* 🎉\n"
                                                  f"👤 Jogador: {data['Likes_Info']['Name']}\n"
                                                  f"🔢 Likes antes: {data['Likes_Info']['Likes before']}\n"
                                                  f"⭐ Likes depois: {data['Likes_Info']['Likes later']}",
                                 parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "❌ *Erro ao enviar likes. Tente novamente mais tarde.*", parse_mode="Markdown")
        except Exception:
            bot.send_message(message.chat.id, "❌ *Erro ao processar a solicitação. Tente novamente mais tarde.*", parse_mode="Markdown")

    Thread(target=process_likes).start()

# Comando /checkban
@bot.message_handler(commands=['checkban'])
def check_ban(message):
    msg_split = message.text.split()
    if len(msg_split) < 2:
        bot.send_message(message.chat.id, "❌ Uso correto: /checkban <ID do jogador>")
        return

    player_id = msg_split[1]
    bot.send_message(message.chat.id, "🔍 *Verificando status de banimento, por favor aguarde...*", parse_mode="Markdown")

    def process_checkban():
        api_url = f"https://api.nowgarena.com/api/check_banned?uid={player_id}"
        try:
            response = requests.get(api_url)
            data = response.json()

            if data.get("status") == "success":
                if data["isBanned"] == "yes":
                    bot.send_message(message.chat.id, f"❌ *Jogador banido!*\n"
                                                      f"🕒 Tempo de banimento: {data['period']} meses",
                                     parse_mode="Markdown")
                else:
                    bot.send_message(message.chat.id, "✅ *Jogador não está banido.*", parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "❌ *Erro ao verificar status de banimento. Tente novamente mais tarde.*", parse_mode="Markdown")
        except Exception:
            bot.send_message(message.chat.id, "❌ *Erro ao processar a solicitação. Tente novamente mais tarde.*", parse_mode="Markdown")

    Thread(target=process_checkban).start()

# Comando /comprarbot
@bot.message_handler(commands=['comprarbot'])
def buy_bot(message):
    bot.send_message(message.chat.id, "💰 Para adquirir este bot, entre em contato: [t.me/werbert_ofc](https://t.me/werbert_ofc)", parse_mode="Markdown")

# Inicia o bot
bot.polling(none_stop=True)