# Version: 0.0.1 | Updated: 2025-03-17 15:06:33 | Branch: DEV | Commit: c6cc354 |  Repo: Juan-glitch/CustomImgSearch
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

def guardar_resultados(imagenes, nombre_archivo='resultados_imagenes.json'):
    """
    Description:
         guardar_resultados function.
    Args:
        imagenes: The first parameter.
        nombre_archivo: The second parameter.
    Returns:
        None
    """
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        json.dump(imagenes, f, ensure_ascii=False, indent=4)
    print(f'Resultados guardados en {nombre_archivo}')

def descargar_imagenes(imagenes, directorio='imagenes_descargadas'):
    """
    Description:
         descargar_imagenes function.
    Args:
        imagenes: The first parameter.
        directorio: The second parameter.
    Returns:
        None
    """
    if not os.path.exists(directorio):
        os.makedirs(directorio)
    for i, imagen in enumerate(imagenes):
        try:
            extension = 'jpg'
            mime = imagen.get('tipo_contenido', '')
            if 'png' in mime:
                extension = 'png'
            elif 'gif' in mime:
                extension = 'gif'
            elif 'svg' in mime:
                extension = 'svg'
            elif 'webp' in mime:
                extension = 'webp'
            nombre_archivo = f'{directorio}/imagen_{i + 1}.{extension}'
            respuesta = requests.get(imagen['enlace'], stream=True, timeout=10)
            if respuesta.status_code == 200:
                with open(nombre_archivo, 'wb') as f:
                    for chunk in respuesta.iter_content(1024):
                        f.write(chunk)
                print(f'Imagen {i + 1} descargada como {nombre_archivo}')
            else:
                print(f'Error al descargar imagen {i + 1}: Codigo {respuesta.status_code}')
        except Exception as e:
            print(f'Error al procesar imagen {i + 1}: {str(e)}')

def load_image(image_path: str) -> Image.Image:
    """
    Description:
         load_image function.
    Args:
        image_path: The first parameter.
    Returns:
        The return value. TODO: Describe return value.
    """
    image = Image.open(image_path)
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    return image

def show_image(image: Image.Image, window_name='Imagen'):
    """
    Description:
         show_image function.
    Args:
        image: The first parameter.
        window_name: The second parameter.
    Returns:
        None
    """
    image_np = np.array(image)
    plt.imshow(image_np)
    plt.show()