from googleapiclient.discovery import build
from datetime import datetime




from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Access your variables
github_username = os.getenv("GITHUB_USERNAME")
github_token = os.getenv("GITHUB_TOKEN")
google_api_key = os.getenv("GOOGLE_API_KEY")

class GoogleSearchEngine:
    def __init__(self, api_key, search_engine_id):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.service = build('customsearch', 'v1', developerKey=api_key)
        self.search_engine_id = search_engine_id

    def buscarImgs(self, query, num_imagenes=10, imgSize="LARGE", tipo="photo", 
                        derechos=None, filetype='png', imgColorType='color'):
        """
        Busca imágenes en Google y devuelve información detallada sobre ellas.
        
        Parámetros:
        - query: Términos de búsqueda
        - num_imagenes: Número de imágenes a buscar (máximo 10 por solicitud)
        - tamaño: Tamaño de imagen ['HUGE', 'ICON', 'LARGE', 'MEDIUM', 'SMALL', 'XLARGE', 'XXLARGE']
            - filtro_tamaño: Filtro de tamaño de imagen en formato 'imagesize:>800x600' mirar doc
        - tipo: Tipo de imagen ('clipart', 'face', 'lineart', 'photo', 'animated')
        - derechos: Filtro de derechos ('cc_publicdomain', 'cc_attribute', 'cc_sharealike', 'cc_noncommercial', 'cc_nonderived')
        - formato: Formato de imagen ('jpg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico', 'raw')
        
        
        Retorna:
        - Lista de diccionarios con información de las imágenes
        """
        
        # Prepara los parámetros de búsqueda
        params = {
            'q': query,
            'cx': self.search_engine_id,
            'searchType': 'image',  # Especifica que solo queremos imágenes
            'num': num_imagenes
        }
        
        # Añade filtros opcionales si se proporcionan
        if imgSize:
            params['imgSize'] = imgSize
        if tipo:
            params['imgType'] = tipo
        if derechos:
            params['rights'] = derechos
        if imgColorType:
            params['imgColorType'] = imgColorType
        if filetype:
            params['fileType'] = filetype
        # Realiza la búsqueda
        res = self.service.cse().list(**params).execute()
        
        # Procesa los resultados y extrae información relevante
        imagenes = []
        for item in res.get('items', []):
            imagen_info = {
                'titulo': item.get('title'),
                'enlace': item.get('link'),
                'thumbnail': item.get('image', {}).get('thumbnailLink'),
                'ancho': item.get('image', {}).get('width'),
                'alto': item.get('image', {}).get('height'),
                'tamaño_bytes': item.get('image', {}).get('byteSize'),
                'tipo_contenido': item.get('mime'),
                'contexto': item.get('image', {}).get('contextLink'),
                'fecha_busqueda': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            imagenes.append(imagen_info)
        
        return imagenes




if __name__ == '__main__':
    import os
    import sys

    # Agrega la ruta raíz del proyecto al path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    sys.path.append(project_root)

    print("Rutas en sys.path:")
    print("\n".join(sys.path))  # Verifica si '/app' está en sys.path
