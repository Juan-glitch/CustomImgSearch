# Guía de Configuración y Uso de Google Custom Search API

## Introducción

En esta guía, aprenderás a configurar y utilizar la Google Custom Search API para realizar búsquedas personalizadas. A continuación, se detallan los pasos necesarios para configurar un motor de búsqueda personalizado, obtener una API Key, y un ejemplo práctico en Python.

## Configuración Inicial

1. **Crear un Motor de Búsqueda Personalizado (Custom Search Engine)**
    - Visita [Google Programmable Search Engine](https://programmablesearchengine.google.com/controlpanel/all)
    - Crea un nuevo motor de búsqueda
    - Configura las opciones según tus necesidades
    - Guarda el ID del motor de búsqueda (Search Engine ID o cx)

2. **Obtener una API Key**
    - Visita la [Google Cloud Console](https://console.cloud.google.com/)
    - Crea un nuevo proyecto o selecciona uno existente
    - Habilita la API de Custom Search
    - Crea credenciales (API Key)
    - La API Key se usará para autenticar tus solicitudes

## Información de la API

- **Límites de uso**: La versión gratuita permite 100 consultas por día
- **Costos**: Consulta la [página de precios](https://developers.google.com/custom-search/v1/overview) para información actualizada
- **Documentación**: Disponible en
from googleapiclient.discovery import build

# Configuración de credenciales
API_KEY = 'AIzaSyCa8rwThH_fzlwMYNFHGEnmhi_x8KUdQ4w'  # Tu API Key
SEARCH_ENGINE_ID = 'TU_SEARCH_ENGINE_ID'  # ID de tu motor de búsqueda

## Requisitos Previos

1. Instalar la biblioteca necesaria:
```bash
pip install google-api-python-client
```

2. Asegurarse de que la API está habilitada en la [Google Cloud Console](https://console.cloud.google.com/apis/library/customsearch.googleapis.com)

# Parámetros Comunes para la API de Google Custom Search

A continuación, te presento una lista de algunos de los parámetros más comunes que puedes incluir en tu solicitud para afinar los resultados:

- **q**: Término(s) de búsqueda. Este parámetro es obligatorio y define la consulta que deseas realizar.
- **cx**: ID del motor de búsqueda personalizado. Este parámetro es obligatorio y especifica el contexto de búsqueda que has configurado en tu CSE.
- **searchType**: Define el tipo de búsqueda. Por ejemplo, para buscar solo imágenes, establece este parámetro en 'image'.
- **num**: Número de resultados que deseas obtener por solicitud. El valor predeterminado es 10, y el máximo permitido es 10.
- **start**: Índice del primer resultado que deseas obtener. Útil para paginar resultados.
- **lr**: Restringe los resultados a un idioma específico. Por ejemplo, 'lang_es' para español.
- **cr**: Filtra los resultados por país. Utiliza el formato 'countryXX', donde 'XX' es el código de país en dos letras (por ejemplo, 'countryES' para España).
- **safe**: Activa el filtro SafeSearch para excluir contenido explícito. Los valores posibles son 'off' (desactivado) y 'active' (activado).
- **dateRestrict**: Restringe los resultados a contenido publicado en un periodo de tiempo específico. Por ejemplo, 'd1' para el último día, 'w1' para la última semana o 'm1' para el último mes.
- **sort**: Ordena los resultados según un criterio específico, como la fecha. Por ejemplo, 'date' para ordenar por fecha.
- **imgSize**: (Solo para búsqueda de imágenes) Filtra imágenes por tamaño. Los valores posibles incluyen:
  - 'icon': Icono (pequeño)
  - 'small': Pequeño
  - 'medium': Mediano
  - 'large': Grande
  - 'xlarge': Extra grande
  - 'xxlarge': Extra extra grande
  - También puedes especificar tamaños en píxeles, por ejemplo, '400x300'
  - Para establecer un tamaño mínimo, puedes usar 'imagesize:>' seguido del tamaño en píxeles, por ejemplo, 'imagesize:>800x600' para imágenes mayores a 800x600 píxeles
- **imgType**: (Solo para búsqueda de imágenes) Filtra imágenes por tipo. Los valores posibles incluyen:
  - 'clipart': Clipart
  - 'face': Rostro
  - 'lineart': Dibujo lineal
  - 'news': Noticias
  - 'photo': Fotografía
- **imgColorType**: (Solo para búsqueda de imágenes) Filtra imágenes por tipo de color. Los valores posibles incluyen:
  - 'color': Color
  - 'gray': Escala de grises
  - 'mono': Monocromo
  - 'trans': Transparente
- **rights**: Filtra los resultados según los derechos de uso. Por ejemplo:
  - 'cc_publicdomain': Dominio público
  - 'cc_attribute': Requiere atribución
  - 'cc_sharealike': Compartir igual
  - 'cc_noncommercial': No comercial
  - 'cc_nonderived': Sin obras derivadas
- **fileType**: Filtra los resultados por tipo de archivo. Los valores posibles incluyen 'pdf', 'doc', 'xls', 'ppt', 'txt', 'rtf', 'swf', 'html', entre otros.
- **hq**: Incluye términos adicionales en la consulta. Es similar a 'q', pero se utiliza para agregar términos adicionales que deben estar presentes en los resultados.
- **gl**: Filtra los resultados por país o región geográfica. Utiliza el código de país en dos letras (por ejemplo, 'ES' para España).
- **hl**: Establece el idioma de la interfaz de usuario para los resultados de búsqueda. Por ejemplo, 'es' para español.
- **exactTerms**: Incluye términos exactos en la consulta. Los resultados deben contener estos términos exactos.
- **excludeTerms**: Excluye términos específicos de la consulta. Los resultados no deben contener estos términos.
- **linkSite**: Limita los resultados a páginas que enlazan a un sitio específico.
- **orTerms**: Incluye términos alternativos en la consulta. Los resultados pueden contener cualquiera de estos términos.

Para una descripción detallada de todos los parámetros disponibles y sus posibles valores, te recomiendo consultar la [documentación oficial de la API de Google Custom Search](https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list).

## Ejemplo de Uso en Python

```python
from googleapiclient.discovery import build

def main():
    # Reemplaza con tu propia información
    API_KEY = 'TU_API_KEY'
    SEARCH_ENGINE_ID = 'TU_SEARCH_ENGINE_ID'
    query = 'imagenesperros'  # Términos de búsqueda

    # Construye el servicio de la API
    service = build('customsearch', 'v1', developerKey=API_KEY)

    # Realiza la búsqueda
    res = service.cse().list(q=query, cx=SEARCH_ENGINE_ID, searchType='image', num=10).execute()

    # Procesa y muestra los resultados
    for item in res.get('items', []):
        title = item.get('title')
        link = item.get('link')
        snippet = item.get('snippet')
        print(f'Título: {title}\nEnlace: {link}\nDescripción: {snippet}\n')

if __name__ == '__main__':
    main()
```