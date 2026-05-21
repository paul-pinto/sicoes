import re
import json
import requests
from bs4 import BeautifulSoup

def extraer_datos_infosiscon(municipio):
    url = f"https://infosiscon.com/buscador/{municipio}.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        filas = soup.find_all('tr')
        convocatorias = []
        
        for fila in filas:
            celdas = fila.find_all('td')
            if len(celdas) >= 5:
                text_entidad = " ".join(celdas[0].text.split())
                
                # Filtro estricto para capturar solo las alcaldías correspondientes
                if "gobierno autonomo municipal" in text_entidad.lower() or "g.a.m." in text_entidad.lower():
                    
                    # 1. Extraer CUCE (Patrón numérico estándar del SICOES: XX-XXXX-XX-XXXXXXX-X-X)
                    match_cuce = re.search(r'\d{2}-\d{4}-\d{2}-\d{7}-\d-\d', text_entidad)
                    cuce = match_cuce.group(0) if match_cuce else "Sin CUCE"
                    
                    # 2. Separar Objeto, Tipo de Contratación y Modalidad
                    text_objeto = " ".join(celdas[1].text.split())
                    
                    # Detectamos la modalidad al final (ej: "- CNC" o "- ANPE")
                    match_modalidad = re.search(r'-\s*([A-Z0-9]+)$', text_objeto)
                    modalidad = match_modalidad.group(1) if match_modalidad else "Ver Detalle"
                    
                    # Limpiamos la modalidad del texto principal
                    objeto = re.sub(r'-\s*[A-Z0-9]+$', '', text_objeto).strip()
                    
                    # Limpiamos el Tipo de Contratación residual que Infosiscon pega al objeto (Bienes/Obras/Servicios)
                    objeto = re.sub(r'(Bienes|Obras|Servicios Generales|Servicios de Consultoría)\s*$', '', objeto, flags=re.IGNORECASE).strip()
                    
                    # 3. Separar Estado y Fechas
                    text_fechas = " ".join(celdas[2].text.split())
                    estado = "Vigente" if "vigente" in text_fechas.lower() else "Concluido"
                    
                    # Extraer fechas con formato DD-MM-AAAA usando regex
                    fechas_encontradas = re.findall(r'\d{2}-\d{2}-\d{4}', text_fechas)
                    fecha_pub = fechas_encontradas[0] if len(fechas_encontradas) > 0 else "No registra"
                    fecha_pres = fechas_encontradas[1] if len(fechas_encontradas) > 1 else "No registra"
                    
                    # 4. Enlace absoluto del botón Detalles
                    link_detalle = ""
                    boton = celdas[4].find('a') if len(celdas) > 4 else None
                    if boton and boton.has_attr('href'):
                        link_detalle = boton['href']
                        if not link_detalle.startswith('http'):
                            link_detalle = f"https://infosiscon.com/{link_detalle.lstrip('/')}"

                    convocatorias.append({
                        "cuce": cuce,
                        "municipio": municipio,
                        "objeto": objeto,
                        "modalidad": modalidad,
                        "estado": estado,
                        "fecha_publicacion": fecha_pub,
                        "fecha_presentacion": fecha_pres,
                        "enlace": link_detalle
                    })
                    
        return convocatorias

    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")
        return []

# Bloque de prueba local independiente
if __name__ == "__main__":
    for muni in ["Riberalta", "Cobija"]:
        print(f"\n==================================================")
        print(f"[EXTRACTOR] Convocatorias para: {muni}")
        print(f"==================================================")
        resultados = extraer_datos_infosiscon(muni)
        print(f"📋 Total encontradas en la tabla: {len(resultados)}\n")
        
        for idx, item in enumerate(resultados, start=1):
            print(f"📌 Convocatoria #{idx}")
            print(f"  ID/CUCE:      {item['cuce']}")
            print(f"  Objeto:       {item['objeto']}")
            print(f"  Modalidad:    {item['modalidad']}")
            print(f"  Publicación:  {item['fecha_publicacion']} | Presentación: {item['fecha_presentacion']}")
            print(f"  Enlace:       {item['enlace']}")
            print(f"--------------------------------------------------")