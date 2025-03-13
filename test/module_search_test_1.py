import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from module_search.class_imgSearch import GoogleSearchEngine
from common.utils import guardar_resultados, descargar_imagenes
import debugpy
from dotenv import load_dotenv, find_dotenv
import os
from module_search.class_imgSearch import GoogleSearchEngine  # Importa el módulo desde la raíz del proyecto

# Permite que VS Code se conecte al depurador
debugpy.listen(("0.0.0.0", 5678))
print("Esperando debugger...")
debugpy.wait_for_client()  # Espera hasta que VS Code se conecte

# Una vez conectado, puedes depurar cualquier    parte del código


print("¡El debugger está activo!")

import json

def test_1():

    # Solicita los términos de búsqueda al usuario
    # query = input("Introduce términos de búsqueda para las imágenes: ")
    query="imagenes de perros"
    # Configuración de búsqueda (puedes ajustar estos parámetros)
    num_imagenes = 5
    tamaño = "LARGE"  # Opciones: 'icon', 'small', 'medium', 'large', 'xlarge', 'xxlarge', 'huge'
    tipo = "photo"    # Opciones: 'clipart', 'face', 'lineart', 'photo', 'animated'

if __name__ == '__main__':
    import os
    import sys



    # Find and load the .env file
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path)
    # Access variables from the .env file

    print(os.getenv("GOOGLE_APIKEY"))  
    print(os.getenv("GOOGLE_CSX"))

    researcher = GoogleSearchEngine(os.getenv("GOOGLE_APIKEY"), os.getenv("GOOGLE_CSX"))
    resultados = researcher.searchImgs("perros", 5, "LARGE", "photo")
          
    # # Busca las imágenes
    
    # Muestra información básica de los resultados
    print("\nResultados encontrados:")
    for i, imagen in enumerate(resultados):
        print(f"Imagen {i+1}:")
        print(f"  Título: {imagen['titulo']}")
        print(f"  Dimensiones: {imagen['ancho']}x{imagen['alto']} píxeles")
        print(f"  Tamaño: {round(int(imagen['tamaño_bytes'])/1024, 2)} KB")
        print(f"  URL: {imagen['enlace']}\n")
        
        # Guarda los resultados en formato JSON
        guardar_resultados(resultados)
        
        # Pregunta si quiere descargar las imágenes
        descargar = input("¿Deseas descargar estas imágenes? (s/n): ").lower()
        if descargar == 's' or descargar == 'si':
            descargar_imagenes(resultados)

if __name__ == '__main__':
    test_1()