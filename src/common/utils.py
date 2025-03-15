import json
import requests
import os
from PIL import Image
import os
import numpy as np
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

from PIL import Image
import numpy as np

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


def load_image(image_path: str) -> Image.Image:
    """
    Carga una imagen desde una ruta y la convierte a RGBA si es necesario.
    
    :param image_path: Ruta de la imagen.
    :return: Objeto PIL.Image en modo RGBA.
    """
    image = Image.open(image_path)
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    return image

def show_image(image: Image.Image, window_name="Imagen"):
    """
    Muestra una imagen usando Matplotlib.
    
    :param image: Objeto PIL.Image a visualizar.
    :param window_name: Título de la ventana.
    """
    # Convertir la imagen PIL a un arreglo NumPy (RGBA)
    image_np = np.array(image)
    
    # Mostrar la imagen usando Matplotlib
    plt.imshow(image_np)
    # plt.title(window_name)
    # plt.axis('off')  # Ocultar los ejes
    plt.show()
