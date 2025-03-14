import os
import sys


print("🗂 Directorio de trabajo actual:", os.getcwd())  # Muestra el directorio desde donde se ejecuta el script
print("\n📂 Contenido del directorio actual:", os.listdir("."))  # Lista archivos y carpetas en la raíz del proyecto
print("\n📂 Contenido de '/app/src':", os.listdir("/app/src") if os.path.exists("/app/src") else "No existe")

print("\n🔍 Rutas de búsqueda en sys.path:")
for p in sys.path:
    print("   ", p)

# Intenta importar el módulo y captura el error si falla
try:
    from module_search_engine.class_searchEngine import GoogleSearchEngine
    print("\n✅ Importación exitosa: module_search.module_imgSearch está accesible.")
except ModuleNotFoundError as e:
    print("\n❌ ERROR:", e)
