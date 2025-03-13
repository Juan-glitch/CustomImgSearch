
import torch
import clip
import torch.nn.functional as F
import torch
import clip
import numpy as np
from PIL import Image
from common.utils import load_image, show_image  # Importamos la función desde common.py
class Embeddings:
    def __init__(self):
        # Detecta si se dispone de GPU y carga el modelo CLIP
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess_clip = clip.load("ViT-B/32", device=self.device)

    def getImgEmbedding(self,  image_path: str) -> torch.Tensor:
        """
        Procesa la imagen con CLIP y devuelve el embedding normalizado.
        :param image: Objeto PIL.Image.
        :return: Tensor normalizado con el embedding.
        """
        image = load_image(image_path)  # Carga la imagen desde common.py
        # show_image(image)  # Abre una ventana emergente con la imagen. Probado en: /app/src/module_embeddings/verify_img_preprocessing.ipynb
        image_tensor = self.preprocess_clip(image).unsqueeze(0).to(self.device)
        image_embedding = self.model.encode_image(image_tensor)
        return image_embedding / image_embedding.norm(dim=-1, keepdim=True)
