import sys
import asyncio
import sqlite3

# IMPORTS DE TUS MÓDULOS
from extractor import extraer_datos_infosiscon
from database import inicializar_db, es_registro_nuevo, guardar_convocatoria
from bot_telegram import enviar_alerta_canal, ejecutar_polling_bot

def ejecutar_cron_monitoreo():
    """Función para automatizar dos veces al día."""
    print("\n[CRON] Iniciando escaneo programado de Infosiscon...")
    inicializar_db()
    
    municipios = ["Riberalta", "Cobija"]
    nuevos_totales = 0
    
    for muni in municipios:
        lista_convocatorias = extraer_datos_infosiscon(muni)
        for item in lista_convocatorias:
            if es_registro_nuevo(item['cuce']):
                guardar_convocatoria(item)
                
                mensaje = (
                    f"🔔 *NUEVA CONVOCATORIA DETECTADA*\n\n"
                    f"🏛️ *Municipio:* {item['municipio'].upper()}\n"
                    f"🆔 *CUCE:* `{item['cuce']}`\n"
                    f"📂 *Modalidad:* {item['modalidad']}\n"
                    f"📝 *Objeto:* {item['objeto']}\n"
                    f"📅 *Publicación:* {item['fecha_publicacion']}\n"
                    f"⏳ *Presentación:* {item['fecha_presentacion']}\n\n"
                    f"🔗 [Abrir Ficha de Licitación]({item['enlace']})"
                )
                
                enviar_alerta_canal(mensaje)
                nuevos_totales += 1
                
    print(f"[CRON] Escaneo finalizado. Alertas enviadas: {nuevos_totales}")

if __name__ == "__main__":
    # SOLUCIÓN CRÍTICA PARA WINDOWS: Forzar la política de bucle asíncrono correcta
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--bot":
            print("[SISTEMA] Inicializando Base de Datos...")
            inicializar_db()
            print("[SISTEMA] Arrancando el Bot de Telegram...")
            ejecutar_polling_bot()
        else:
            ejecutar_cron_monitoreo()
            
    except Exception as error:
        print("\n❌ ¡OCURRIÓ UN ERROR CRÍTICO AL ARRANCAR!")
        print(f"Detalle técnico del error: {error}")
        import traceback
        traceback.print_exc()