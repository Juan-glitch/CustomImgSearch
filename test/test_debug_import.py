# Version: 0.0.1 | Updated: 2025-03-17 15:06:31 | Branch: DEV | Commit: c6cc354 |  Repo: Juan-glitch/CustomImgSearch
import os
import sys
print('🗂 Directorio de trabajo actual:', os.getcwd())
print('\n📂 Contenido del directorio actual:', os.listdir('.'))
print("\n📂 Contenido de '/app/src':", os.listdir('/app/src') if os.path.exists('/app/src') else 'No existe')
print('\n🔍 Rutas de busqueda en sys.path:')
for p in sys.path:
    print('   ', p)
try:
    from module_search_engine.class_searchEngine import GoogleSearchEngine
    print('\n✅ Importacion exitosa: module_search.module_imgSearch esta accesible.')
except ModuleNotFoundError as e:
    print('\n❌ ERROR:', e)