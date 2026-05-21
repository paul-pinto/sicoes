import sqlite3

DB_NAME = "licitaciones.db"

def inicializar_db():
    """Crea la tabla si no existe en el sistema."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS convocatorias (
            cuce TEXT PRIMARY KEY,
            municipio TEXT,
            objeto TEXT,
            modalidad TEXT,
            fecha_publicacion TEXT,
            fecha_presentacion TEXT,
            enlace TEXT,
            notificado INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def es_registro_nuevo(cuce):
    """Devuelve True si el CUCE no existe en la base de datos."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM convocatorias WHERE cuce = ?", (cuce,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado is None

def guardar_convocatoria(item):
    """Guarda la convocatoria y la marca como notificada (1)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO convocatorias 
            (cuce, municipio, objeto, modalidad, fecha_publicacion, fecha_presentacion, enlace, notificado) 
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (
            item['cuce'], item['municipio'], item['objeto'], 
            item['modalidad'], item['fecha_publicacion'], 
            item['fecha_presentacion'], item['enlace']
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Por si se intenta duplicar por error de concurrencia
    conn.close()