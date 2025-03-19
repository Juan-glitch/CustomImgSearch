# Version: 0.0.1 | Updated: 2025-03-17 15:06:31 | Branch: DEV | Commit: c6cc354 |  Repo: Juan-glitch/CustomImgSearch
from googleapiclient.discovery import build
from datetime import datetime
from dotenv import load_dotenv
import os
load_dotenv()
github_username = os.getenv('GITHUB_USERNAME')
github_token = os.getenv('GITHUB_TOKEN')
google_api_key = os.getenv('GOOGLE_API_KEY')

class GoogleSearchEngine:

    def __init__(self, api_key, search_engine_id):
        """
        Description:
             __init__ function.
        Args:
            api_key: The first parameter.
            search_engine_id: The second parameter.
        """
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.service = build('customsearch', 'v1', developerKey=api_key)
        self.search_engine_id = search_engine_id

    def searchImgs(self, query, num_imagenes=10, imgSize='LARGE',
                    tipo='photo', derechos=None, filetype='png',
                    imgColorType='color'):
        """
        Description:
             searchImgs function.
        Args:
            query: The first parameter.
            num_imagenes: The second parameter.
            imgSize: The third parameter.
            tipo: The fourth parameter.
            derechos: The fifth parameter.
            filetype: The sixth parameter.
            imgColorType: The seventh parameter.
        Returns:
            None
        """
        params = {'q': query, 'cx': self.search_engine_id, 'searchType': 'image', 'num': num_imagenes}
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
        res = self.service.cse().list(**params).execute()
        imagenes = []
        for item in res.get('items', []):
            imagen_info = {'titulo': item.get('title'), 'enlace': item.get('link'), 'thumbnail': item.get('image', {}).get('thumbnailLink'), 'ancho': item.get('image', {}).get('width'), 'alto': item.get('image', {}).get('height'), 'tamaño_bytes': item.get('image', {}).get('byteSize'), 'tipo_contenido': item.get('mime'), 'contexto': item.get('image', {}).get('contextLink'), 'fecha_busqueda': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            imagenes.append(imagen_info)
        return imagenes

    def extract_links(self, query, num_imagenes=10, imgSize='LARGE',
                       tipo='photo', derechos=None, filetype='png',
                       imgColorType='color'):
        """
        Description:
             extract_links function.
        Args:
            query: The first parameter.
            num_imagenes: The second parameter.
            imgSize: The third parameter.
            tipo: The fourth parameter.
            derechos: The fifth parameter.
            filetype: The sixth parameter.
            imgColorType: The seventh parameter.
        Returns:
            None
        """
        resultados = self.searchImgs(query, num_imagenes, imgSize, tipo, derechos, filetype, imgColorType)
        links = [item.get('enlace') for item in resultados if item.get('enlace')]
        return links