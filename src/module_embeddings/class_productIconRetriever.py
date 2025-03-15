import torch
import numpy as np
import requests
import logging
import re
import time
from typing import Optional, List, Dict, Any, Union
from openai import OpenAI
from tqdm import tqdm
import clip
from PIL import Image
from io import BytesIO

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductIconRetriever:
    """
    Clase especializada para recuperar enlaces a imágenes que pueden servir como
    iconos de productos de repostería basados en embeddings visuales, utilizando
    la tipología de mensajes compatible con modelos o1 y GPT-4.5. Además, se
    integra el modelo CLIP para evaluar la similitud entre el embedding original y
    el contenido visual de las imágenes.
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.2,
        max_tokens: int = 5000,  # Valor inicial para max_completion_tokens
        validate_urls: bool = True,
        cache_results: bool = True,
        similarity_threshold: float = 0.6  # Umbral de similitud para aceptar una imagen
    ):
        """
        Inicializa el recuperador de iconos de producto.

        Args:
            api_key: Clave de API de OpenAI.
            model: Modelo a utilizar.
            temperature: Temperatura para las respuestas del modelo.
            max_tokens: Máximo número de tokens en la respuesta (se mapea a max_completion_tokens).
            validate_urls: Si se validan las URLs obtenidas.
            cache_results: Si se guardan los resultados en caché.
            similarity_threshold: Valor mínimo de similitud para aceptar un enlace.
        """
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.validate_urls = validate_urls
        self.cache_results = cache_results
        self.similarity_threshold = similarity_threshold

        # Se crea el objeto cliente de OpenAI una sola vez
        self.client = OpenAI(api_key=api_key)

        # Inicializar caché
        self._cache = {}

        # Prompt template
        self.chat_prompt_template = (
            "Necesito encontrar {num_links} imágenes que puedan servir como iconos de productos de repostería, "
            "basadas en la siguiente representación vectorial:\n\n"
            "{embedding_representation}\n\n"
            "{context_info}"
            "Las imágenes deben cumplir estos requisitos:\n"
            "- Mostrar el producto completo\n"
            "- Buena iluminación y enfoque\n"
            "- Fondo neutro o transparente\n"
            "- Resolución adecuada para iconos\n"
            "- Detalles claros de textura, color y decoración\n\n"
            "La respuesta debe estar en el siguiente formato EXACTO:\n"
            "1:\n[URL del enlace 1]\n"
            "2:\n[URL del enlace 2]\n"
            "...\n"
            "N:\n[URL del enlace N]"
        )

        # Mensaje de sistema (para modelos que lo soportan)
        self.system_message = "Eres un especialista en encontrar imágenes para iconos de productos de repostería."

        # Cargar modelo CLIP y preprocesador
        try:
            self.clip_device = "cuda" if torch.cuda.is_available() else "cpu"
            self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.clip_device)
            logger.info("Modelo CLIP cargado exitosamente.")
        except Exception as e:
            logger.error("Error cargando el modelo CLIP: " + str(e))
            self.clip_model = None
            self.clip_preprocess = None

    def _embedding_to_visual_representation(self, embedding: Union[torch.Tensor, np.ndarray]) -> str:
        """
        Convierte un embedding en una representación detallada que maximiza la información visual
        contenida para la búsqueda de imágenes de productos.
        """
        if isinstance(embedding, np.ndarray):
            embedding = torch.from_numpy(embedding)
        embedding = embedding.flatten()
        normalized_emb = embedding / (torch.norm(embedding) + 1e-8)
        significant_dims = 50
        truncated = normalized_emb[:significant_dims]
        detailed_repr = ", ".join([f"{x:.8f}" for x in truncated.tolist()])

        embedding_stats = {
            "media": torch.mean(embedding).item(),
            "desviación": torch.std(embedding).item(),
            "max": torch.max(embedding).item(),
            "min": torch.min(embedding).item(),
            "rango_dinámico": (torch.max(embedding) - torch.min(embedding)).item(),
        }
        stats_repr = "\n".join([f"- {key}: {value:.6f}" for key, value in embedding_stats.items()])

        return (
            f"Vector de embedding (primeras {significant_dims} dimensiones):\n"
            f"[{detailed_repr}]\n\n"
            f"Estadísticas del embedding completo:\n{stats_repr}\n\n"
        )

    def _parse_image_links(self, response_text: str) -> List[str]:
        """
        Extrae y filtra enlaces de imágenes de la respuesta del modelo.
        """
        url_pattern = r'https?://[^\s<>"\']+(?:\.[^\s<>"\']+)+(?:[^\s.,<>"\'()]|\([^\s<>"\']*\))*'
        urls = re.findall(url_pattern, response_text)
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')
        product_image_domains = (
            'imgur.com', 'cloudfront.net', 'cloudinary.com', 'unsplash.com',
            'shutterstock.com', 'istockphoto.com', 'gettyimages.com', 'adobe.stock.com',
            'freepik.com', 'pexels.com', 'pixabay.com',
            'images-amazon.com', 'walmart.com', 'target.com', 'shopify.com',
            'ebayimg.com', 'cdn.shopify.com', 'alibaba.com', 'alicdn.com'
        )
        valid_links = []
        for url in urls:
            if any(url.lower().endswith(ext) for ext in image_extensions):
                valid_links.append(url)
            elif any(domain in url.lower() for domain in product_image_domains):
                valid_links.append(url)
        if not valid_links:
            for line in response_text.splitlines():
                line = line.strip()
                if line.startswith('http') and '://' in line:
                    url = line.split(' ')[0]
                    valid_links.append(url)
        return valid_links

    def _is_valid_image_url(self, url: str) -> bool:
        """Verifica si una URL apunta a una imagen válida y accesible."""
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                return 'image' in content_type.lower()
            return False
        except Exception as e:
            logger.debug(f"Error validando URL {url}: {e}")
            return False

    def _validate_image_urls(self, urls: List[str]) -> List[str]:
        """Valida una lista de URLs de imágenes."""
        if not self.validate_urls or not urls:
            return urls
        valid_urls = []
        for url in urls:
            if self._is_valid_image_url(url):
                valid_urls.append(url)
        return valid_urls

    def _compute_similarity(self, original_embedding: torch.Tensor, image_url: str) -> float:
        """
        Calcula la similitud entre el embedding original y el embedding de la imagen obtenido con CLIP.
        Se descarga la imagen, se preprocesa y se computa el embedding.
        """
        if self.clip_model is None or self.clip_preprocess is None:
            logger.error("Modelo CLIP no está disponible.")
            return 0.0

        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content)).convert("RGB")
        except Exception as e:
            logger.error(f"Error al descargar o abrir la imagen: {image_url} - {e}")
            return 0.0

        try:
            image_input = self.clip_preprocess(image).unsqueeze(0).to(self.clip_device)
            with torch.no_grad():
                image_embedding = self.clip_model.encode_image(image_input)
            image_embedding = image_embedding / image_embedding.norm(dim=-1, keepdim=True)

            # Normalizar el embedding original
            if original_embedding.ndim == 1:
                original_norm = original_embedding / original_embedding.norm()
            else:
                original_norm = original_embedding / original_embedding.norm(dim=-1, keepdim=True)
            similarity = (image_embedding @ original_norm.T).item()
            return similarity
        except Exception as e:
            logger.error(f"Error al procesar la imagen con CLIP: {image_url} - {e}")
            return 0.0

    def _get_cache_key(self, embedding: Union[torch.Tensor, np.ndarray], num_links: int) -> str:
        """Genera una clave única para el caché."""
        if isinstance(embedding, np.ndarray):
            embedding = torch.from_numpy(embedding)
        emb_values = embedding.flatten()[:10].tolist()
        emb_str = "_".join([f"{x:.4f}" for x in emb_values])
        return f"{emb_str}_{num_links}"

    def find_product_images(
        self,
        embedding: Union[torch.Tensor, np.ndarray],
        num_links: int = 5,
        product_description: Optional[str] = None,
        force_refresh: bool = False,
        max_attempts: int = 3  # Número máximo de reintentos para ajustar tokens
    ) -> Dict[str, Any]:
        if self.cache_results and not force_refresh:
            cache_key = self._get_cache_key(embedding, num_links)
            if cache_key in self._cache:
                logger.info("Resultado recuperado de caché")
                return self._cache[cache_key]

        # Convertir el embedding a una representación visual detallada
        embedding_repr = self._embedding_to_visual_representation(embedding)

        # Preparar contexto adicional si existe la descripción del producto
        context_info = f"Descripción del producto: {product_description}\n\n" if product_description else ""

        # Construir el prompt final con instrucción reforzada
        final_prompt = (
            self.chat_prompt_template.format(
                num_links=num_links,
                embedding_representation=embedding_repr,
                context_info=context_info
            )
            + "\n\nPor favor, responde únicamente con las URLs de las imágenes en el formato EXACTO indicado."
        )

        # Crear la lista de mensajes según el modelo
        if self.model.startswith('o1'):
            messages = [{"role": "user", "content": final_prompt}]
        else:
            messages = [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": final_prompt}
            ]

        # Forzar temperatura 1 para modelos o1
        effective_temperature = 1 if self.model.startswith("o1") else self.temperature

        attempt = 1
        current_max_tokens = self.max_tokens
        filtered_links = []
        while attempt <= max_attempts:
            logger.info(f"Intento {attempt} con max_completion_tokens = {current_max_tokens}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_completion_tokens=current_max_tokens,
                temperature=effective_temperature
            )
            choice = response.choices[0]
            finish_reason = choice.finish_reason
            response_text = choice.message.content.strip()
            logger.info("Respuesta del modelo:\n" + response_text)

            # Parsear enlaces
            image_links = self._parse_image_links(response_text)
            logger.info(f"Enlaces extraídos sin filtrar: {image_links}")

            # Filtrar enlaces: validar URL y calcular similitud mediante CLIP
            filtered_links = []
            for link in image_links:
                if self._is_valid_image_url(link):
                    sim = self._compute_similarity(embedding, link)
                    logger.info(f"Similitud para {link}: {sim}")
                    if sim >= self.similarity_threshold:
                        filtered_links.append(link)
            logger.info(f"Enlaces filtrados (similares y válidos): {filtered_links}")

            # Si se obtuvo el número de enlaces deseados, salir del bucle
            if len(filtered_links) >= num_links:
                break
            else:
                attempt += 1
                current_max_tokens = int(current_max_tokens * 1.5)
                logger.info("Reintentando con mayor cantidad de tokens.")

        result = {
            "links": filtered_links,
            "num_requested": num_links,
            "num_found": len(filtered_links),
            "success": True,
            "model": self.model,
            "timestamp": time.time()
        }

        if self.cache_results:
            cache_key = self._get_cache_key(embedding, num_links)
            self._cache[cache_key] = result

        return result

    def batch_find_images(
        self,
        embeddings: List[Union[torch.Tensor, np.ndarray]],
        show_progress: bool = True,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Procesa múltiples embeddings para encontrar imágenes de productos.

        Args:
            embeddings: Lista de embeddings.
            show_progress: Mostrar barra de progreso.
            **kwargs: Parámetros adicionales para find_product_images.

        Returns:
            Lista de resultados.
        """
        results = []
        iterator = tqdm(embeddings, desc="Buscando imágenes") if show_progress else embeddings

        for emb in iterator:
            result = self.find_product_images(emb, **kwargs)
            results.append(result)

        return results

    def clear_cache(self):
        """Limpia la caché de resultados."""
        self._cache = {}
        logger.info("Caché limpiada")

    def export_results(self, results: Union[Dict[str, Any], List[Dict[str, Any]]], filename: str):
        """
        Exporta los resultados a un archivo de texto.

        Args:
            results: Resultado único o lista de resultados.
            filename: Nombre del archivo de salida.
        """
        if isinstance(results, dict):
            results = [results]

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=== RESULTADOS DE BÚSQUEDA DE ICONOS DE PRODUCTO ===\n\n")

            for i, result in enumerate(results, 1):
                f.write(f"RESULTADO #{i}\n")
                f.write(f"Éxito: {'Sí' if result.get('success', False) else 'No'}\n")
                f.write(f"Modelo: {result.get('model', 'N/A')}\n")
                f.write(f"Enlaces encontrados: {result.get('num_found', 0)}/{result.get('num_requested', 0)}\n")

                if 'error' in result:
                    f.write(f"Error: {result['error']}\n")

                if result.get('links', []):
                    f.write("\nENLACES:\n")
                    for j, link in enumerate(result['links'], 1):
                        f.write(f"{j}. {link}\n")

                f.write("\n" + "-"*50 + "\n\n")

        logger.info(f"Resultados exportados a {filename}")
