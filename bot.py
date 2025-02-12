import asyncio
import logging
import os
import subprocess
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Cargar las variables de entorno
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Configuración del bot y logging
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
router = Router()

# Configurar el scheduler para tareas automáticas
scheduler = AsyncIOScheduler()

# Variable global para almacenar el chat_id
user_chat_id = None

# Ruta del directorio de backups
BACKUP_DIR = "./backup"

# Comando de inicio: Guarda el chat_id
@router.message(F.text == "/start")
async def send_welcome(message: Message):
    global user_chat_id
    user_chat_id = message.chat.id  # Guardar el chat_id del usuario
    await message.answer("¡Hola! Soy tu bot de monitoreo. 😊\nUsa /status para verificar el estado del servidor.")
    logging.info(f"Chat ID guardado: {user_chat_id}")

# Comando de estado del servidor (en tiempo real)
@router.message(F.text == "/status")
async def server_status(message: Message):
    status = get_docker_status()
    backup_status = check_backup()
    await message.answer(f"Estado del servidor Docker:\n{status}\n\nÚltimo Backup:\n{backup_status}")

# Función para obtener el estado de Docker
def get_docker_status():
    try:
        result = subprocess.run(["docker", "ps", "--format", "{{.Names}}: {{.Status}}"], capture_output=True, text=True)
        if result.stdout:
            return result.stdout.strip()
        else:
            return "No hay contenedores en ejecución. ❌"
    except Exception as e:
        return f"Error al obtener el estado del servidor: {e}"

# Función para verificar el estado del backup
def check_backup():
    try:
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        latest_backup = None

        # Verificar si hay archivos de backup recientes
        for file in os.listdir(BACKUP_DIR):
            file_path = os.path.join(BACKUP_DIR, file)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_time > one_hour_ago:
                latest_backup = file
                break

        if latest_backup:
            return f"Backup reciente detectado: {latest_backup} ✅"
        else:
            return "No se encontró un backup reciente. ⚠️"
    except Exception as e:
        return f"Error al verificar los backups: {e}"

# Tarea automática para enviar alertas cada hora
async def scheduled_status():
    global user_chat_id
    if user_chat_id:  # Verificar si ya se guardó el chat_id
        status = get_docker_status()
        backup_status = check_backup()
        await bot.send_message(user_chat_id, f"🔔 Alerta Automática\n\nEstado del servidor Docker:\n{status}\n\nÚltimo Backup:\n{backup_status}")
    else:
        logging.warning("No se ha guardado un chat_id. No se enviarán alertas automáticas.")

# Configurar el job programado
scheduler.add_job(scheduled_status, "interval", hours=1)

# Echo handler (para mensajes no reconocidos)
@router.message()
async def echo(message: Message):
    await message.answer("Comando no reconocido. Usa /start para ver las opciones disponibles.")

# Registro de rutas
dp.include_router(router)

# Función principal para ejecutar el bot
async def main():
    logging.info("Iniciando bot...")
    scheduler.start()  # Iniciar el scheduler
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
