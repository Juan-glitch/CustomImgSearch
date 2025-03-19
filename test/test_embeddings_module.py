# Version: 0.0.1 | Updated: 2025-03-17 15:06:32 | Branch: DEV | Commit: c6cc354 |  Repo: Juan-glitch/CustomImgSearch
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from module_embeddings.class_embedinnizer import Embeddings
from module_embeddings.class_embeddingDescriber import EmbeddingDescriber
import os
from dotenv import find_dotenv, load_dotenv
from module_embeddings.utils_embeddings import list_openai_models

if __name__ == '__main__':
    # Find and load the .env file
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path)

    # Lista los modelos disponibles de la api de OpenAI
    # list_openai_models(os.getenv("OPENAI_APIKEY"))
    
    # Carga el modelo y el tokenizador
    embeddings = Embeddings()
    embeddingTranslator = EmbeddingDescriber(os.getenv("OPENAI_APIKEY"), os.getenv("OPENAI_MODEL"))
    # Carga una imagen
    image_path = "Imagenes_Panes/Image072.png"
    image_tensor = embeddings.getImgEmbedding(image_path)

    # Extrae la descripción de la imagen
    description = embeddingTranslator.extractDescription(image_embedding = image_tensor,
                                                         additional_context= 'Iconos de productos de panaderia y pasteleria y reposteria',
                                                         theme = 'Productos panaderia y pasteleria',
                                                         search_engine = 'google_images')
    print(description)