# Version: 0.0.1 | Updated: 2025-03-17 15:06:32 | Branch: DEV | Commit: c6cc354 |  Repo: Juan-glitch/CustomImgSearch
import torch
import clip
import torch.nn.functional as F
import torch
import clip
import numpy as np
from PIL import Image
from common.utils import load_image, show_image

class Embeddings:

    def __init__(self):
        """
        Description:
             __init__ function.
        Args:
        """
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model, self.preprocess_clip = clip.load('ViT-B/32', device=self.device)

    def getImgEmbedding(self, image_path: str) -> torch.Tensor:
        """
        Description:
             getImgEmbedding function.
        Args:
            image_path: The first parameter.
        Returns:
            The return value. TODO: Describe return value.
        """
        image = load_image(image_path)
        image_tensor = self.preprocess_clip(image).unsqueeze(0).to(self.device)
        image_embedding = self.model.encode_image(image_tensor)
        return image_embedding / image_embedding.norm(dim=-1, keepdim=True)