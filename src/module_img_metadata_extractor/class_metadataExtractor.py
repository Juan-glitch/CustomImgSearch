# Version: 0.0.1 | Updated: 2025-03-17 15:06:30 | Branch: DEV | Commit: c6cc354 |  Repo: Juan-glitch/CustomImgSearch
import os
import json
import requests

class MetadataExtractor:
    """
    Clase para almacenar toda la informacion procesada de una imagen.
    """

    def __init__(self, image_path, embedding, description, search_results):
        """
        Description:
             __init__ function.
        Args:
            image_path: The first parameter.
            embedding: The second parameter.
            description: The third parameter.
            search_results: The fourth parameter.
        """
        self.image_path = image_path
        self.embedding = embedding
        self.description = description
        self.search_results = search_results
        self.downloaded_files = []

    def to_dict(self):
        """
        Description:
             to_dict function.
        Args:
        Returns:
            None
        """
        emb = self.embedding.tolist() if hasattr(self.embedding, 'tolist') else self.embedding
        return {'image_path': self.image_path, 'embedding': emb, 'description': self.description, 'search_results': self.search_results, 'downloaded_files': self.downloaded_files}

    def save_metadata(self, output_dir):
        """
        Description:
             save_metadata function.
        Args:
            output_dir: The first parameter.
        Returns:
            None
        """
        metadata_path = os.path.join(output_dir, 'metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

def download_image(url, dest_path):
    """
    Description:
         download_image function.
    Args:
        url: The first parameter.
        dest_path: The second parameter.
    Returns:
        None
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(dest_path, 'wb') as f:
                f.write(response.content)
            return dest_path
        else:
            print(f'Error al descargar {url}: status {response.status_code}')
            return None
    except Exception as e:
        print(f'Excepcion al descargar {url}: {e}')
        return None

def process_image(image_path, embeddings, embeddingTranslator, researcher,
                   base_output_dir):
    """
    Description:
         process_image function.
    Args:
        image_path: The first parameter.
        embeddings: The second parameter.
        embeddingTranslator: The third parameter.
        researcher: The fourth parameter.
        base_output_dir: The fifth parameter.
    Returns:
        None
    """
    print(f'Procesando {image_path}...')
    image_embedding = embeddings.getImgEmbedding(image_path)
    description = embeddingTranslator.extractDescription(image_embedding=image_embedding, additional_context='Iconos de productos de panaderia y pasteleria y reposteria', theme='Productos panaderia y pasteleria', search_engine='google_images')
    search_results = researcher.searchImgs(description, 5, 'LARGE', 'photo')
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    image_dir = os.path.join(base_output_dir, image_name)
    os.makedirs(image_dir, exist_ok=True)
    processed_image = process_image(image_path, image_embedding, description, search_results)
    for idx, url in enumerate(search_results):
        filename = f'downloaded_{idx}.jpg'
        dest_path = os.path.join(image_dir, filename)
        downloaded = download_image(url, dest_path)
        if downloaded:
            processed_image.downloaded_files.append(downloaded)
    processed_image.save_metadata(image_dir)
    return processed_image