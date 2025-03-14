import os
import json
import requests


class MetadataExtractor:
    """
    Clase para almacenar toda la información procesada de una imagen.
    """
    def __init__(self, image_path, embedding, description, search_results):
        self.image_path = image_path
        self.embedding = embedding
        self.description = description
        self.search_results = search_results    
        self.downloaded_files = []  # rutas locales de las imágenes descargadas

    def to_dict(self):
        # Si el embedding es un array de numpy, conviértelo a lista.
        emb = self.embedding.tolist() if hasattr(self.embedding, "tolist") else self.embedding
        return {
            "image_path": self.image_path,
            "embedding": emb,
            "description": self.description,
            "search_results": self.search_results,
            "downloaded_files": self.downloaded_files,
        }

    def save_metadata(self, output_dir):
        """
        Guarda la metadata de la imagen en formato JSON en el directorio output_dir.
        """
        metadata_path = os.path.join(output_dir, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)


def download_image(url, dest_path):
    """
    Descarga una imagen desde la URL y la guarda en dest_path.
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(dest_path, "wb") as f:
                f.write(response.content)
            return dest_path
        else:
            print(f"Error al descargar {url}: status {response.status_code}")
            return None
    except Exception as e:
        print(f"Excepción al descargar {url}: {e}")
        return None


def process_image(image_path, embeddings, embeddingTranslator, researcher, base_output_dir):
    """
    Procesa una imagen:
      1. Obtiene su embedding.
      2. Extrae la descripción.
      3. Realiza la búsqueda y obtiene links.
      4. Descarga las imágenes y guarda la metadata.
    """
    print(f"Procesando {image_path}...")
    # 1. Obtener el embedding de la imagen
    image_embedding = embeddings.getImgEmbedding(image_path)

    # 2. Extraer la descripción de la imagen
    description = embeddingTranslator.extractDescription(
        image_embedding=image_embedding,
        additional_context='Iconos de productos de panaderia y pasteleria y reposteria',
        theme='Productos panaderia y pasteleria',
        search_engine='google_images'
    )

    # 3. Buscar imágenes similares (obtenemos 5 links)
    search_results = researcher.searchImgs(description, 5, "LARGE", "photo")

    # 4. Crear un directorio específico para esta imagen (basado en su nombre)
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    image_dir = os.path.join(base_output_dir, image_name)
    os.makedirs(image_dir, exist_ok=True)

    # Crear el objeto ProcessedImage
    processed_image = process_image(image_path, image_embedding, description, search_results)

    # 5. Descargar las imágenes obtenidas
    for idx, url in enumerate(search_results):
        filename = f"downloaded_{idx}.jpg"  # podrías ajustar la extensión si es necesario
        dest_path = os.path.join(image_dir, filename)
        downloaded = download_image(url, dest_path)
        if downloaded:
            processed_image.downloaded_files.append(downloaded)

    # 6. Guardar la metadata en un archivo JSON
    processed_image.save_metadata(image_dir)

    return processed_image


