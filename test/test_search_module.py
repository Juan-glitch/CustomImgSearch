import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from common.utils import guardar_resultados, descargar_imagenes
from dotenv import load_dotenv, find_dotenv
import os
from module_search_engine.class_searchEngine import GoogleSearchEngine  # Importa el módulo desde la raíz del proyecto


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

    query = 'perros'
    researcher = GoogleSearchEngine(os.getenv("GOOGLE_APIKEY"), os.getenv("GOOGLE_CSX"))
    resultados = researcher.searchImgs(query, 5, "LARGE", "photo")
          
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

    links = researcher.extract_links(query, num_imagenes=5)
    print("Links extraídos:")
    for link in links:
        print(link)   

if __name__ == '__main__':
    test_1()