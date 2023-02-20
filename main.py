import requests
import json
import telebot

# Definindo a chave da API OpenAI, token do bot e modelos a serem usados
API_KEY = "SECRET_KEY_AQUI"
BOT_TOKEN = "TOKEN_DO_BOT_AQUI"
MODEL_TEXT = "text-davinci-003"
MODEL_IMAGE = "image-alpha-001"

# Definindo os parâmetros para geração de texto
MAX_TOKENS = 960
TEMPERATURE = 0.5

def generate_text(prompt):
    if len(prompt) > 4096: # verificação do limite de caracteres do Telegram
        return "O prompt é muito longo. Por favor, tente novamente com um prompt mais curto."
        
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
    try:
        # Definindo a URL da API e os headers para fazer a requisição
        url = "https://api.openai.com/v1/images/generations"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

        # Definindo os dados a serem enviados na requisição
        data = {"model": MODEL_IMAGE, "prompt": prompt, "n": n, "size": size}

        # Fazendo a requisição e verificando se ocorreu algum erro
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_json = response.json()
        if "error" in response_json:
            return f"Error: {response_json['error']['message']}"

        # Se não houve erro, retornar as URLs das imagens geradas
        urls = [image["url"] for image in response_json["data"]]
        return urls

    except Exception as e:
        # Retornando uma mensagem de erro em caso de exceção
        return f"Error: {e}"


# Iniciando o bot do Telegram
bot = telebot.TeleBot(BOT_TOKEN)

# Definindo as funções que serão executadas quando o usuário enviar um comando
@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.reply_to(message, "Olá, eu sou um bot que gera texto e imagem a partir de textos. Digite /help para saber como me usar.")

@bot.message_handler(commands=['help'])
def send_welcome(message):
    help_message = "Olá! Eu sou o ChatGPT, um bot de bate-papo alimentado pelo modelo de linguagem GPT. \n\nAqui estão os comandos que eu entendo:\n/start - Inicia o bot\n/help - Exibe esta mensagem de ajuda\n/image [prompt] - Gera uma imagem a partir do prompt fornecido\n/text [prompt] - Gera um texto a partir do prompt fornecido\n/tweet [prompt] - Gera um tweet a partir do prompt fornecido\n\nDigite um comando para começar!"
    bot.send_message(message.chat.id, help_message)

@bot.message_handler(commands=["text"])
def handle_text(message):
    user_text = message.text[6:].strip()
    generated_text = generate_text(user_text)
    bot.reply_to(message, generated_text)

@bot.message_handler(commands=["image"])
def handle_image(message):
    user_text = message.text[6:].strip()
    generated_image_urls = generate_image(user_text)
    if isinstance(generated_image_urls, str):
        # Se a resposta da API OpenAI contém um erro, envia a mensagem de erro para o usuário
        bot.reply_to(message, generated_image_urls)
    else:
        for url in generated_image_urls:
            bot.send_photo(message.chat.id, url)

@bot.message_handler(commands=["tweet"])
def handle_tweet(message):
    user_text = message.text[7:].strip()
    prompt = f"resuma isso em um tweet de até 140 caracteres em português: {user_text}"
    generated_text = generate_text(prompt)
    tweet = generated_text
    bot.reply_to(message, tweet)

# Iniciando o processo de escutar mensagens do bot
bot.polling()