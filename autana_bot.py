import logging
import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configuración Inicial ---
TOKEN = '8477264282:AAFqTyyTd-Y9d3QF9SMXt7eHJ3ro6C0pBxE'  # ¡Asegúrate de poner tu token aquí!
bot = Bot(token=TOKEN)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Creamos la aplicación del bot UNA SOLA VEZ ---
# y le añadimos los manejadores de comandos
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="¡Hola! Soy Autana Bot. ¡Esta es la versión final y corregida!"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_recibido = update.message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Recibí tu mensaje: {texto_recibido}"
    )

application.add_handler(CommandHandler('start', start))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))


# --- La App Web (Flask) ---
app = Flask(__name__)

@app.route(f'/{TOKEN}', methods=['POST'])
async def webhook():
    # Esta función se activa cada vez que Telegram envía un mensaje
    update_data = request.get_json()
    update = Update.de_json(update_data, bot)
    
    # Procesamos el mensaje usando la aplicación que ya creamos
    await application.process_update(update)
    
    return 'ok'

# Esta función es para configurar el webhook cuando el servidor inicie
def setup():
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        application.bot.set_webhook(f'{render_url}/{TOKEN}')
        logging.info(f'Webhook configurado en {render_url}')

# Esto asegura que la configuración se ejecute una sola vez al iniciar
setup()