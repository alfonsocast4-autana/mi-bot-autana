import logging
import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, Application

# Tu token de Telegram
TOKEN = '8477264282:AAFqTyyTd-Y9d3QF9SMXt7eHJ3ro6C0pBxE'

# Configuración básica del bot
bot = Bot(token=TOKEN)

# Configuración para ver logs (mensajes de estado)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- Nuestras funciones de siempre ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="¡Hola! Soy Autana Bot, ahora funcionando con Webhooks en Render."
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_recibido = update.message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=texto_recibido
    )

# --- La nueva parte para la App Web ---
app = Flask(__name__)

@app.route(f'/{TOKEN}', methods=['POST'])
async def webhook():
    json_str = request.get_json()
    update = Update.de_json(json_str, bot)
    
    # Creamos una aplicación temporal para procesar el update
    # Esto es necesario porque la librería está diseñada para un loop constante,
    # y aquí solo procesamos un evento a la vez.
    temp_app = ApplicationBuilder().token(TOKEN).build()
    
    # Aquí es donde le decimos qué hacer con los mensajes
    temp_app.add_handler(CommandHandler('start', start))
    temp_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
    
    await temp_app.process_update(update)
    return 'ok'

# Esta función es para configurar el webhook cuando el servidor inicie
def setup():
    # Obtenemos la URL de nuestro servicio en Render (se establece automáticamente)
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        # Le decimos a Telegram dónde enviar los updates
        bot.set_webhook(f'{render_url}/{TOKEN}')
        logging.info(f'Webhook configurado en {render_url}')

# Esto asegura que la configuración se ejecute una sola vez al iniciar
setup()

# El servidor Flask no soporta 'async' de forma nativa,
# así que no lo ejecutamos directamente con app.run().
# Render usará un servidor como Gunicorn para correr esto.