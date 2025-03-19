# Version: 0.0.1 | Updated: 2025-03-17 15:06:30 | Branch: DEV | Commit: c6cc354 |  Repo: Juan-glitch/CustomImgSearch
import torch
from typing import Optional, Dict, Any, List
from openai import OpenAI

class EmbeddingDescriber:

    def __init__(self, api_key: Optional[str]=None, model: str='gpt-4o',
                  max_tokens: int=100):
        """
        Description:
             __init__ function.
        Args:
            api_key: The first parameter.
            model: The second parameter.
            max_tokens: The third parameter.
        """
        self.model = model
        self.max_tokens = max_tokens
        self.client = OpenAI(api_key=api_key)
        self.prompt_templates = {'general': 'Genera una descripcion detallada y especifica para buscar imagenes similares en Google.', 'producto': "Describe este producto con terminos especificos, incluyendo caracteristicas distintivas. Si se trata de productos de panaderia, bolleria o pasteleria, utiliza formatos como:\n\nPara pan:\n- 'Pan de panaderia redondo similar a una hogaza, con corteza ligeramente dorada y cortes en forma de estrella'.\n- 'Pan alargado estilo baguette, con corteza crujiente y miga aireada'.\n- 'Pan rustico estilo chapata, con corteza gruesa y cortes diagonales anchos que resaltan su caracter artesanal'.\n\nPara bolleria:\n- 'Croissant hojaldrado, con capas doradas y textura ligera, perfecto para un desayuno elegante'.\n- 'Bollo de crema, con relleno suave y cobertura glaseada, que destaca por su forma y presentacion'.\n\nPara pasteleria:\n- 'Pastel de chocolate con capas esponjosas y decoracion sofisticada, realzado por detalles en ganache'.\n- 'Tarta de frutas frescas con base crujiente y combinacion armonica de sabores, decorada con glaseado sutil'.\n\nPara macarons:\n- 'Macarons apilados en diferentes colores pastel, como rosa, amarillo, verde y naranja. Los macarons tienen una textura suave y ligeramente crujiente por fuera, con un relleno cremoso visible entre las capas'.\n\nAsegurate de mencionar detalles visuales clave como la textura, la forma, los colores y cualquier patron o decoracion distintiva.", 'persona': 'Describe a esta persona usando detalles visuales clave: rasgos faciales, estilo de ropa, postura y ambiente.', 'paisaje': 'Describe este paisaje con detalles especificos: clima, vegetacion, iluminacion y cualquier elemento arquitectonico o natural relevante.'}

    def _embedding2str(self, embedding: torch.Tensor) -> str:
        """
        Description:
             _embedding2str function.
        Args:
            embedding: The first parameter.
        Returns:
            The return value. TODO: Describe return value.
        """
        truncated = embedding.flatten()[:20]
        return ', '.join([f'{x:.16f}' for x in truncated.tolist()])

    def _clean_description(self, text: str) -> str:
        """
        Description:
             _clean_description function.
        Args:
            text: The first parameter.
        Returns:
            The return value. TODO: Describe return value.
        """
        text = text.replace('1.', '').replace('1:', '').replace('2.', '').replace('2:', '').strip()
        return text

    def _parse_response(self, response_text: str) -> Dict[str, str]:
        """
        Description:
             _parse_response function.
        Args:
            response_text: The first parameter.
        Returns:
            The return value. TODO: Describe return value.
        """
        concise_description = ''
        detailed_description = ''
        if '1.' in response_text and '2.' in response_text:
            parts = response_text.split('2.')
        elif '1:' in response_text and '2:' in response_text:
            parts = response_text.split('2:')
        else:
            parts = response_text.split('\n\n2:')
        if len(parts) == 2:
            concise_description = self._clean_description(parts[0])
            detailed_description = self._clean_description(parts[1])
        else:
            concise_description = response_text[:100]
            detailed_description = response_text
        return {'concise_description': concise_description, 'detailed_description': detailed_description}

    def extractDescription(self, image_embedding: torch.Tensor, image_type: str='producto', additional_context: Optional[str]=None, search_engine: str='google_images', theme: Optional[str]=None) -> Dict[str, Any]:
        """
        Description:
             extractDescription function.
        Args:
            image_embedding: The first parameter.
            image_type: The second parameter.
            additional_context: The third parameter.
            search_engine: The fourth parameter.
            theme: The fifth parameter.
        Returns:
            The return value. TODO: Describe return value.
        """
        embedding_str = self._embedding2str(image_embedding)
        template = self.prompt_templates.get(image_type, self.prompt_templates)
        search_specific_tips = ''
        if search_engine == 'google_images':
            search_specific_tips = 'Optimiza para Google Images usando terminos especificos.'
        context_info = f'\nContexto adicional: {additional_context}' if additional_context else ''
        theme_info = f'\nAplica el siguiente tema a la descripcion: {theme}' if theme else ''
        output_format = 'La respuesta debe estar en el siguiente formato EXACTO:\n1:\n[Descripcion concisa, maximo 15 palabras]\n\n2:\n[Descripcion detallada, maximo 30 palabras]'
        prompt = f'Representacion vectorial de una imagen:\n[{embedding_str}]\n{context_info}{theme_info}\n\n{template}\n\n{search_specific_tips}\n\n{output_format}'
        prompt = f'Representacion vectorial de una imagen:\n[{embedding_str}]\n{context_info}{theme_info}\n\n{template}\n\n{search_specific_tips}\n\n{output_format}'
        try:
            response = self.client.chat.completions.create(model=self.model, messages=[{'role': 'system', 'content': 'Eres un experto en analisis visual de imagenes.'}, {'role': 'user', 'content': prompt}])
            description_text = response.choices[0].message.content.strip()
            parsed_response = self._parse_response(description_text)
            result = {'concise_description': parsed_response['concise_description'], 'detailed_description': parsed_response['detailed_description'], 'full_response': description_text, 'image_type': image_type, 'search_engine': search_engine, 'theme': theme, 'model_used': self.model}
        except Exception as e:
            result = {'error': True, 'message': f'Error al generar la descripcion: {str(e)}', 'image_type': image_type, 'search_engine': search_engine}
        return result

    def batch_process(self, embeddings: List[torch.Tensor], **kwargs) -> List[Dict[str, Any]]:
        """
        Description:
             batch_process function.
        Args:
            embeddings: The first parameter.
        Returns:
            The return value. TODO: Describe return value.
        """
        results = []
        for embedding in embeddings:
            result = self.extractDescription(embedding, **kwargs)
            results.append(result)
        return results