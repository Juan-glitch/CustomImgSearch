import torchvision.transforms as transforms
from PIL import Image
import torch
import clip
from openai import OpenAI
import os

def list_openai_models(openai_apikey: str = None):
    """
    Muestra los modelos disponibles en OpenAI.

    Requiere la clave de API en la variable de entorno OPENAI_API_KEY.
    """
    # Configurar la clave de API
    if openai_apikey is None:
        print("ERROR: No se encontro  la clave de API en la variable de entorno OPENAI_API_KEY")
        return
    # Crear el cliente de OpenAI
    client = OpenAI(
    api_key=openai_apikey  # this is also the default, it can be omitted
    )
    # Listar los modelos disponibles
    models = client.models.list()
    for model in models.data:
        print(model.id)
