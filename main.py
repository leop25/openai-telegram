import requests
import json
import telebot

# Definindo a chave da API OpenAI, token do bot e modelos a serem usados
API_KEY = "SECRET_KEY_AQUI"
BOT_TOKEN = "TOKEN_DO_BOT_AQUI"
MODEL_TEXT = "text-davinci-003"
MODEL_IMAGE = "image-alpha-001"

# Definindo os parâmetros para geração de texto
MAX_TOKENS = 50
TEMPERATURE = 0.5

def generate_text(prompt):
    # Definindo a URL da API e os headers para fazer a requisição
    url = "https://api.openai.com/v1/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

    # Definindo os dados a serem enviados na requisição
    data = {"model": MODEL_TEXT, "prompt": prompt, "temperature": TEMPERATURE, "max_tokens": MAX_TOKENS}

    # Fazendo a requisição e retornando o texto gerado ou uma mensagem de erro
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        text = response.json()["choices"][0]["text"]
        return text.strip()
    else:
        return f"Error: {response.status_code}"

def generate_image(prompt, n=1, size="512x512"):
    # Definindo a URL da API e os headers para fazer a requisição
    url = "https://api.openai.com/v1/images/generations"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

    # Definindo os dados a serem enviados na requisição
    data = {"model": MODEL_IMAGE, "prompt": prompt, "n": n, "size": size}

    # Fazendo a requisição e retornando as URLs das imagens geradas ou uma mensagem de erro
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        urls = [image["url"] for image in response.json()["data"]]
        return urls
    else:
        return f"Error: {response.status_code}"

# Iniciando o bot do Telegram
bot = telebot.TeleBot(BOT_TOKEN)

# Definindo as funções que serão executadas quando o usuário enviar um comando
@bot.message_handler(commands=["text"])
def handle_text(message):
    user_text = message.text[6:].strip()
    generated_text = generate_text(user_text)
    bot.reply_to(message, generated_text)

@bot.message_handler(commands=["image"])
def handle_image(message):
    user_text = message.text[6:].strip()
    generated_image_urls = generate_image(user_text)
    for url in generated_image_urls:
        bot.send_photo(message.chat.id, url)

# Iniciando o processo de escutar mensagens do bot
bot.polling()
