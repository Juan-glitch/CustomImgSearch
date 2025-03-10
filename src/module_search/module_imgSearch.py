from googleapiclient.discovery import build
from datetime import datetime
from common import guardar_resultados, descargar_imagenes


class GoogleSearchEngine:

def buscar_imagenes(query, num_imagenes=10, imgSize="LARGE", tipo="photo", 
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
    # Reemplaza con tu propia información
    API_KEY = 'your google apikey'
    SEARCH_ENGINE_ID = 'your created search engine id'
    # Construye el servicio de la API
    service = build('customsearch', 'v1', developerKey=API_KEY)
    
    # Prepara los parámetros de búsqueda
    params = {
        'q': query,
        'cx': SEARCH_ENGINE_ID,
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
    res = service.cse().list(**params).execute()
    
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




