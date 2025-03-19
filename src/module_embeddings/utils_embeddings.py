# Version: 0.0.1 | Updated: 2025-03-17 15:06:30 | Branch: DEV | Commit: c6cc354 |  Repo: Juan-glitch/CustomImgSearch
import torchvision.transforms as transforms
from PIL import Image
import torch
import clip
from openai import OpenAI
import os

def list_openai_models(openai_apikey: str=None):
    """
    Description:
         list_openai_models function.
    Args:
        openai_apikey: The first parameter.
    Returns:
        None
    """
    if openai_apikey is None:
        print('ERROR: No se encontro  la clave de API en la variable de entorno OPENAI_API_KEY')
        return
    client = OpenAI(api_key=openai_apikey)
    models = client.models.list()
    for model in models.data:
        print(model.id)