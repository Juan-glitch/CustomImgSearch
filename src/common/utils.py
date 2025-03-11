import json
import requests
import os

def guardar_resultados(imagenes, nombre_archivo="resultados_imagenes.json"):
    """
    Guarda los resultados de la búsqueda en un archivo JSON.
    """
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        json.dump(imagenes, f, ensure_ascii=False, indent=4)
    print(f"Resultados guardados en {nombre_archivo}")

def descargar_imagenes(imagenes, directorio="imagenes_descargadas"):
    """
    Descarga las imágenes encontradas en un directorio especificado.
    """
    # Crea el directorio si no existe
    if not os.path.exists(directorio):
        os.makedirs(directorio)
    
    for i, imagen in enumerate(imagenes):
        try:
            # Determina la extensión del archivo basado en el tipo MIME
            extension = "jpg"  # Por defecto
            mime = imagen.get('tipo_contenido', '')
            if 'png' in mime:
                extension = "png"
            elif 'gif' in mime:
                extension = "gif"
            elif 'svg' in mime:
                extension = "svg"
            elif 'webp' in mime:
                extension = "webp"
            
            # Construye el nombre del archivo
            nombre_archivo = f"{directorio}/imagen_{i+1}.{extension}"
            
            # Descarga la imagen
            respuesta = requests.get(imagen['enlace'], stream=True, timeout=10)
            if respuesta.status_code == 200:
                with open(nombre_archivo, 'wb') as f:
                    for chunk in respuesta.iter_content(1024):
                        f.write(chunk)
                print(f"Imagen {i+1} descargada como {nombre_archivo}")
            else:
                print(f"Error al descargar imagen {i+1}: Código {respuesta.status_code}")
        except Exception as e:
            print(f"Error al procesar imagen {i+1}: {str(e)}")