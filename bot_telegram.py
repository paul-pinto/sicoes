import sqlite3
import requests
import os  # Requerido para leer variables de entorno
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_model, load_dotenv  # Requerido para cargar el archivo .env

# Cargar las variables del archivo .env si existe
load_dotenv()

# ==========================================
# CONFIGURACIÓN DE CREDENCIALES (SEGURAS)
# ==========================================
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Leemos la cadena de IDs y la transformamos en una lista de enteros
raw_chat_ids = os.getenv("TELEGRAM_CHAT_IDS", "")
CHAT_IDS = [int(id.strip()) for id in raw_chat_ids.split(",") if id.strip().isdigit()]

def enviar_alerta_canal(msg):
    """Envía notificaciones instantáneas de forma pasiva a todos los CHAT_IDS configurados."""
    if not TOKEN or not CHAT_IDS:
        print("⚠️ [ERROR] Faltan configuraciones de Telegram (TOKEN o CHAT_IDS) en el entorno.")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    for chat_id in CHAT_IDS:
        payload = {
            "chat_id": chat_id, 
            "text": msg, 
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code != 200:
                print(f"⚠️ Telegram retornó código de estado {response.status_code} para el ID: {chat_id}")
        except Exception as e:
            print(f"❌ Error al enviar notificación a Telegram para el ID {chat_id}: {e}")