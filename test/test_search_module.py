# Version: 0.0.1 | Updated: 2025-03-17 15:06:32 | Branch: DEV | Commit: c6cc354 |  Repo: Juan-glitch/CustomImgSearch
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from common.utils import guardar_resultados, descargar_imagenes
from dotenv import load_dotenv, find_dotenv
import os
from module_search_engine.class_searchEngine import GoogleSearchEngine

def test_1():
    """
    Description:
         test_1 function.
    Args:
    Returns:
        None
    """
    query = 'imagenes de perros'
    num_imagenes = 5
    tamaño = 'LARGE'
    tipo = 'photo'
if __name__ == '__main__':
    import os
    import sys
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path)
    print(os.getenv('GOOGLE_APIKEY'))
    print(os.getenv('GOOGLE_CSX'))
    query = 'perros'
    researcher = GoogleSearchEngine(os.getenv('GOOGLE_APIKEY'), os.getenv('GOOGLE_CSX'))
    resultados = researcher.searchImgs(query, 5, 'LARGE', 'photo')
    print('\nResultados encontrados:')
    for i, imagen in enumerate(resultados):
        print(f'Imagen {i + 1}:')
        print(f"  Titulo: {imagen['titulo']}")
        print(f"  Dimensiones: {imagen['ancho']}x{imagen['alto']} pixeles")
        print(f"  Tamaño: {round(int(imagen['tamaño_bytes']) / 1024, 2)} KB")
        print(f"  URL: {imagen['enlace']}\n")
        guardar_resultados(resultados)
        descargar = input('¿Deseas descargar estas imagenes? (s/n): ').lower()
        if descargar == 's' or descargar == 'si':
            descargar_imagenes(resultados)
    links = researcher.extract_links(query, num_imagenes=5)
    print('Links extraidos:')
    for link in links:
        print(link)
if __name__ == '__main__':
    test_1()
'Nuevo docstring'