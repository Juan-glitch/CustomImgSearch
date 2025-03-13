import torch
from typing import Optional, Dict, Any, List
from openai import OpenAI

class EmbeddingDescriber:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o", max_tokens: int = 100):
        self.model = model
        self.max_tokens = max_tokens
        self.client = OpenAI(api_key=api_key)
        
        self.prompt_templates = {
            "general": (
                "Genera una descripción detallada y específica para buscar imágenes similares en Google."
            ),
            "producto": (
                "Describe este producto con términos específicos, incluyendo características distintivas. "
                "Si se trata de productos de panadería, bollería o pastelería, utiliza formatos como:\n\n"
                "Para pan:\n"
                "- 'Pan de panadería redondo similar a una hogaza, con corteza ligeramente dorada y cortes en forma de estrella'.\n"
                "- 'Pan alargado estilo baguette, con corteza crujiente y miga aireada'.\n"
                "- 'Pan rústico estilo chapata, con corteza gruesa y cortes diagonales anchos que resaltan su carácter artesanal'.\n\n"
                "Para bollería:\n"
                "- 'Croissant hojaldrado, con capas doradas y textura ligera, perfecto para un desayuno elegante'.\n"
                "- 'Bollo de crema, con relleno suave y cobertura glaseada, que destaca por su forma y presentación'.\n\n"
                "Para pastelería:\n"
                "- 'Pastel de chocolate con capas esponjosas y decoración sofisticada, realzado por detalles en ganache'.\n"
                "- 'Tarta de frutas frescas con base crujiente y combinación armónica de sabores, decorada con glaseado sutil'.\n\n"
                "Para macarons:\n"
                "- 'Macarons apilados en diferentes colores pastel, como rosa, amarillo, verde y naranja. "
                "Los macarons tienen una textura suave y ligeramente crujiente por fuera, con un relleno cremoso visible entre las capas'.\n\n"
                "Asegúrate de mencionar detalles visuales clave como la textura, la forma, los colores y cualquier patrón o decoración distintiva."
            ),
            "persona": (
                "Describe a esta persona usando detalles visuales clave: rasgos faciales, estilo de ropa, postura y ambiente."
            ),
            "paisaje": (
                "Describe este paisaje con detalles específicos: clima, vegetación, iluminación y cualquier elemento arquitectónico o natural relevante."
            )
        }

    def _embedding2str(self, embedding: torch.Tensor) -> str:
        truncated = embedding.flatten()[:20]
        return ", ".join([f"{x:.16f}" for x in truncated.tolist()])

    def _clean_description(self, text: str) -> str:
        """Limpia la descripción eliminando etiquetas numéricas y espacios extra."""
        text = text.replace("1.", "").replace("1:", "").replace("2.", "").replace("2:", "").strip()
        return text
    def _parse_response(self, response_text: str) -> Dict[str, str]:
        """
        Extrae la descripción concisa y detallada de la respuesta del modelo.
        """
        concise_description = ""
        detailed_description = ""

        # Intentamos dividir la respuesta en base a los separadores esperados
        if "1." in response_text and "2." in response_text:
            parts = response_text.split("2.")
        elif "1:" in response_text and "2:" in response_text:
            parts = response_text.split("2:")
        else:
            parts = response_text.split("\n\n2:")  # Captura saltos de línea inesperados

        # Asignamos las partes procesadas
        if len(parts) == 2:
            concise_description = self._clean_description(parts[0])
            detailed_description = self._clean_description(parts[1])
        else:
            # Si no encuentra el formato esperado, asigna valores genéricos
            concise_description = response_text[:100]  # Trunca la primera parte
            detailed_description = response_text

        return {
            "concise_description": concise_description,
            "detailed_description": detailed_description
        }

    def extractDescription(
        self, 
        image_embedding: torch.Tensor, 
        image_type: str = "producto",
        additional_context: Optional[str] = None, 
        search_engine: str = "google_images",
        theme: Optional[str] = None
    ) -> Dict[str, Any]:
        embedding_str = self._embedding2str(image_embedding)
        template = self.prompt_templates.get(image_type, self.prompt_templates)
        
        search_specific_tips = ""
        if search_engine == "google_images":
            search_specific_tips = "Optimiza para Google Images usando términos específicos."
        
        context_info = f"\nContexto adicional: {additional_context}" if additional_context else ""
        theme_info = f"\nAplica el siguiente tema a la descripción: {theme}" if theme else ""
        
        # Se añade la instrucción para el formato exacto de salida
        output_format = (
            "La respuesta debe estar en el siguiente formato EXACTO:\n"
            "1:\n"
            "[Descripción concisa, máximo 15 palabras]\n\n"
            "2:\n"
            "[Descripción detallada, máximo 30 palabras]"
        )
        
        prompt = (
            f"Representación vectorial de una imagen:\n[{embedding_str}]\n"
            f"{context_info}{theme_info}\n\n"
            f"{template}\n\n"
            f"{search_specific_tips}\n\n"
            f"{output_format}"
        )
        prompt = (
            f"Representación vectorial de una imagen:\n[{embedding_str}]\n"
            f"{context_info}{theme_info}\n\n"
            f"{template}\n\n"
            f"{search_specific_tips}\n\n"
            f"{output_format}"
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis visual de imágenes."},
                    {"role": "user", "content": prompt}
                ],
                # max_completion_tokens = self.max_tokens,
            )
            
            description_text = response.choices[0].message.content.strip()
            parsed_response = self._parse_response(description_text)

            result = {
                "concise_description": parsed_response["concise_description"],
                "detailed_description": parsed_response["detailed_description"],
                "full_response": description_text,
                "image_type": image_type,
                "search_engine": search_engine,
                "theme": theme,
                "model_used": self.model
            }
        except Exception as e:
            result = {
                "error": True,
                "message": f"Error al generar la descripción: {str(e)}",
                "image_type": image_type,
                "search_engine": search_engine
            }

        return result
    
    def batch_process(self, embeddings: List[torch.Tensor], **kwargs) -> List[Dict[str, Any]]:
        results = []
        for embedding in embeddings:
            result = self.extractDescription(embedding, **kwargs)
            results.append(result)
        return results
