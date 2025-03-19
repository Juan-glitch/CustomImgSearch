# Version: 0.0.1 | Updated: 2025-03-17 15:06:30 | Branch: DEV | Commit: c6cc354 |  Repo: Juan-glitch/CustomImgSearch
import sys
import os
from dotenv import find_dotenv, load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
# Custom Classes
from module_embeddings.class_embedinnizer import Embeddings
from module_embeddings.class_embeddingDescriber import EmbeddingDescriber
from module_search_engine.class_searchEngine import GoogleSearchEngine
from module_folder_data_explorer.class_folderDataExporer import FolderDataExporter


#########################################
# Bloque principal (main)
#########################################
if __name__ == '__main__':
    # Definir las rutas al inicio para mayor claridad
    OUTPUT_FOLDER = "output_folder"
    METADATA_FILE = os.path.join(OUTPUT_FOLDER, "_img_metadata.csv")
    FOLDER_PATH = "Imagenes_Panes"
    
    # Carga de variables de entorno
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path)

    # Inicialización de modelos y servicios
    embeddings = Embeddings()
    embeddingTranslator = EmbeddingDescriber(os.getenv('OPENAI_APIKEY'), os.getenv('OPENAI_MODEL'))
    researcher = GoogleSearchEngine(os.getenv('GOOGLE_APIKEY'), os.getenv('GOOGLE_CSX'))
    exporter = FolderDataExporter(FOLDER_PATH, OUTPUT_FOLDER)
    
    
    # Data of the different images
    data = []
    extra_context = ('Iconos de productos de panaderia, pasteleria y reposteria. Analiza bien las imagenes para no equivocarte en diferencias productos de panaderia, pasteleria y reposteria.',)
    theme = ('Productos panaderia y pasteleria',)
    search_engine = 'google_images'
    exporter.update_data_range(embeddings=embeddings, embeddingTranslator=embeddingTranslator, researcher=researcher, file_range=[0, 3], extra_context=extra_context, theme=theme, search_engine=search_engine)