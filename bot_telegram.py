import sqlite3
import requests
import os  # Requerido para leer variables de entorno
from datetime import datetime
from zoneinfo import ZoneInfo  # Nativo en Python 3.9+
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv  # Requerido para cargar el archivo .env

# Cargar las variables del archivo .env si existe
load_dotenv()

# ==========================================
# CONFIGURACIÓN DE CREDENCIALES (SEGURAS)
# ==========================================
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Leemos la cadena de IDs y la transformamos en una lista de enteros limpia
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

# ==========================================
# COMANDOS INTERACTIVOS DEL BOT
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Menú principal."""
    await update.message.reply_text(
        "🏛️ *Sistema de Monitoreo SICOES (Infosiscon)*\n"
        "Configurado con la zona horaria de Bolivia (GMT-4).\n\n"
        "*Comandos de consulta manual disponibles:*\n"
        "⏳ /vigentes - Licitaciones cuya fecha de presentación no ha vencido.\n"
        "⛵ /riberalta - Últimas convocatorias del GAM de Riberalta.\n"
        "🐊 /cobija - Últimas convocatorias del GAM de Cobija.\n"
        "🔍 /buscar [palabra] - Buscar por término clave en los objetos (ej: /buscar cemento)",
        parse_mode="Markdown"
    )

async def vigentes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /vigentes - Filtra las licitaciones activas."""
    conn = sqlite3.connect("licitaciones.db")
    cursor = conn.cursor()
    cursor.execute("SELECT cuce, municipio, objeto, modalidad, fecha_presentacion, enlace FROM convocatorias")
    filas = cursor.fetchall()
    conn.close()

    # Forzamos la zona horaria de Bolivia (America/La_Paz)
    tz_bolivia = ZoneInfo("America/La_Paz")
    hoy = datetime.now(tz_bolivia).replace(tzinfo=None)

    encontradas = []

    for f in filas:
        try:
            fecha_limite = datetime.strptime(f[4], "%d-%m-%Y")
            if fecha_limite >= hoy:
                encontradas.append(f)
        except ValueError:
            encontradas.append(f)

    if not encontradas:
        await update.message.reply_text("ℹ️ No se encontraron convocatorias vigentes en la base de datos actualmente.")
        return

    respuesta = f"⏳ *CONVOCATORIAS VIGENTES EN BOLIVIA ({len(encontradas)}):*\n\n"
    for f in encontradas[:10]:
        respuesta += (
            f"🏛️ *{f[1].upper()}* | `{f[0]}`\n"
            f"📂 *{f[3]}:* {f[2][:120]}...\n"
            f"⏳ Límite: *{f[4]}*\n"
            f"🔗 [Ver Detalles del Proceso]({f[5]})\n\n"
            f"----------------------------------------\n\n"
        )
    
    await update.message.reply_text(respuesta, parse_mode="Markdown", disable_web_page_preview=True)

async def cmd_municipio(update: Update, context: ContextTypes.DEFAULT_TYPE, municipio):
    """Función genérica para consultar las últimas 5 convocatorias de un municipio específico."""
    conn = sqlite3.connect("licitaciones.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT cuce, objeto, modalidad, fecha_presentacion, enlace 
        FROM convocatorias WHERE LOWER(municipio) = ? 
        ORDER BY fecha_publicacion DESC LIMIT 5
    ''', (municipio.lower(),))
    filas = cursor.fetchall()
    conn.close()

    if not filas:
        await update.message.reply_text(f"ℹ️ No tengo registros en la BD para {municipio.capitalize()}.")
        return

    respuesta = f"📋 *Últimas 5 convocatorias de {municipio.capitalize()}:*\n\n"
    for f in filas:
        respuesta += (
            f"🆔 `{f[0]}`\n"
            f"📝 *{f[2]}:* {f[1][:130]}...\n"
            f"⏳ Presentación: {f[3]}\n"
            f"🔗 [Ficha Infosiscon]({f[4]})\n\n"
        )
    
    await update.message.reply_text(respuesta, parse_mode="Markdown", disable_web_page_preview=True)

async def riberalta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /riberalta."""
    await cmd_municipio(update, context, "Riberalta")

async def cobija(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /cobija."""
    await cmd_municipio(update, context, "Cobija")

async def buscar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /buscar - Permite encontrar palabras clave dentro del objeto de la licitación."""
    if not context.args:
        await update.message.reply_text("💡 Por favor, ingresa un término. Ejemplo: `/buscar medicamento`", parse_mode="Markdown")
        return
        
    term = "%" + " ".join(context.args).lower() + "%"
    
    conn = sqlite3.connect("licitaciones.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT municipio, cuce, objeto, enlace FROM convocatorias 
        WHERE LOWER(objeto) LIKE ? ORDER BY fecha_publicacion DESC LIMIT 5
    ''', (term,))
    filas = cursor.fetchall()
    conn.close()

    if not filas:
        await update.message.reply_text("🔍 No se encontraron coincidencias en la base de datos.")
        return

    respuesta = "🔍 *Coincidencias encontradas en el historial:*\n\n"
    for f in filas:
        respuesta += f"🏛️ *{f[0].upper()}:* `{f[1]}`\n📝 {f[2][:100]}...\n🔗 [Ver Enlace]({f[3]})\n\n"
        
    await update.message.reply_text(respuesta, parse_mode="Markdown", disable_web_page_preview=True)

def ejecutar_polling_bot():
    """Inicializa la escucha activa bloqueando el hilo principal correctamente."""
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("vigentes", vigentes))
    app.add_handler(CommandHandler("riberalta", riberalta))
    app.add_handler(CommandHandler("cobija", cobija))
    app.add_handler(CommandHandler("buscar", buscar))
    
    print("[BOT] Motor de comandos en línea. Escuchando en Telegram...")
    # run_polling detiene la ejecución aquí para quedarse escuchando de forma asíncrona
    app.run_polling(close_loop=False)