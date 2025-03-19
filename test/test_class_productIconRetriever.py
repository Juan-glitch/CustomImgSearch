# Version: 0.0.1 | Updated: 2025-03-17 15:06:30 | Branch: DEV | Commit: c6cc354 |  Repo: Juan-glitch/CustomImgSearch
import sys
import os
from dotenv import find_dotenv, load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from module_embeddings.class_embedinnizer import Embeddings
from module_embeddings.class_embeddingDescriber import EmbeddingDescriber
from module_search_engine.class_searchEngine import GoogleSearchEngine
from module_folder_data_explorer.class_folderDataExporer import FolderDataExporter
from module_folder_data_explorer.class_csvNavigator import CSVDataNavigator
from module_embeddings.class_productIconRetriever import ProductIconRetriever
from module_embeddings.utils_embeddings import list_openai_models
#########################################
# Bloque principal (main)
#########################################
if __name__ == '__main__':
    OUTPUT_FOLDER = 'output_folder'
    METADATA_FILE = os.path.join(OUTPUT_FOLDER, '_img_metadata.csv')
    FOLDER_PATH = 'Imagenes_Panes'
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path)
    embeddings = Embeddings()
    productRetriever = ProductIconRetriever(os.getenv('OPENAI_APIKEY'), os.getenv('OPENAI_MODEL'))
    navigator = CSVDataNavigator(METADATA_FILE)
    row_data = navigator.get_row_properties(0, ['directory', 'file_name', 'search_links'])
    extra_context = ('Iconos de productos de panaderia, pasteleria y reposteria. Analiza bien las imagenes para no equivocarte en diferencias productos de panaderia, pasteleria y reposteria.',)
    theme = ('Productos panaderia y pasteleria',)
    search_engine = 'google_images'
    embedding = embeddings.getImgEmbedding(os.path.join(row_data['directory'], row_data['file_name']))
    results = productRetriever.find_product_images(embedding, num_links=5, product_description=extra_context, force_refresh=False)
    print(f"\nSe encontraron {results['num_found']} imagenes:")
    for i, link in enumerate(results['links'], 1):
        print(f'{i}. {link}')
