import debugpy
# from module_search.module_imgSearch import GoogleSearchEngine 
# Cargar Variables del entorno
from dotenv import load_dotenv, find_dotenv
import os
from module_search.module_imgSearch import GoogleSearchEngine
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

    # Muestra la ruta de acceso actual (directorio de trabajo)
    current_path = os.getcwd()
    print(f"Ruta de acceso actual: {current_path}")

    # Find and load the .env file
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path)
    # Access variables from the .env file

    print(os.getenv("GOOGLE_APIKEY"))  
    print(os.getenv("GOOGLE_CSX"))

    GoogleSearchEngine(os.getenv("GOOGLE_APIKEY"), os.getenv("GOOGLE_CSX"))
    # GoogleSearchEngine(os.getenv("GOOGLE_APIKEY"), os.getenv("GOOGLE_CSX"))
          
        # # Busca las imágenes
        # print(f"Buscando {num_imagenes} imágenes de '{query}'...")
        # resultados = buscar_imagenes(query, num_imagenes, tamaño, tipo)
        
        # # Muestra información básica de los resultados
        # print("\nResultados encontrados:")
        # for i, imagen in enumerate(resultados):
        #     print(f"Imagen {i+1}:")
        #     print(f"  Título: {imagen['titulo']}")
        #     print(f"  Dimensiones: {imagen['ancho']}x{imagen['alto']} píxeles")
        #     print(f"  Tamaño: {round(int(imagen['tamaño_bytes'])/1024, 2)} KB")
        #     print(f"  URL: {imagen['enlace']}\n")
        
        # # Guarda los resultados en formato JSON
        # guardar_resultados(resultados)
        
        # # Pregunta si quiere descargar las imágenes
        # descargar = input("¿Deseas descargar estas imágenes? (s/n): ").lower()
        # if descargar == 's' or descargar == 'si':
        #     descargar_imagenes(resultados)

if __name__ == '__main__':
    test_1()