import debugpy

# Permite que VS Code se conecte al depurador
debugpy.listen(("0.0.0.0", 5678))
print("Esperando debugger...")
debugpy.wait_for_client()  # Espera hasta que VS Code se conecte

# Una vez conectado, puedes depurar cualquier    parte del código


print("¡El debugger está activo!")


from module_search import module_imgSearch
from common.utils import buscar_imagenes, guardar_resultados, descargar_imagenes 
import json

def test_1():
    # Solicita los términos de búsqueda al usuario
    # query = input("Introduce términos de búsqueda para las imágenes: ")
    query="imagenes de perros"
    # Configuración de búsqueda (puedes ajustar estos parámetros)
    num_imagenes = 5
    tamaño = "LARGE"  # Opciones: 'icon', 'small', 'medium', 'large', 'xlarge', 'xxlarge', 'huge'
    tipo = "photo"    # Opciones: 'clipart', 'face', 'lineart', 'photo', 'animated'
    
    # Busca las imágenes
    print(f"Buscando {num_imagenes} imágenes de '{query}'...")
    resultados = buscar_imagenes(query, num_imagenes, tamaño, tipo)
    
    # Muestra información básica de los resultados
    print("\nResultados encontrados:")
    for i, imagen in enumerate(resultados):
        print(f"Imagen {i+1}:")
        print(f"  Título: {imagen['titulo']}")
        print(f"  Dimensiones: {imagen['ancho']}x{imagen['alto']} píxeles")
        print(f"  Tamaño: {round(int(imagen['tamaño_bytes'])/1024, 2)} KB")
        print(f"  URL: {imagen['enlace']}\n")
    
    # Guarda los resultados en formato JSON
    guardar_resultados(resultados)
    
    # Pregunta si quiere descargar las imágenes
    descargar = input("¿Deseas descargar estas imágenes? (s/n): ").lower()
    if descargar == 's' or descargar == 'si':
        descargar_imagenes(resultados)

if __name__ == '__main__':
    test_1()