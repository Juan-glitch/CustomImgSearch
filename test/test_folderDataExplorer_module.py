import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from module_folder_data_explorer.class_folderDataExporer import FolderDataExporter

# Ejemplo de uso:
if __name__ == '__main__':
    # Ruta de la carpeta con imágenes que se van a procesar
    folder_path = "Imagenes_Panes"  
    # Instancia del exportador de datos, especificando el formato de salida (csv, json o yml)
    exporter = FolderDataExporter(folder_path, output_format='csv')  
    # Procesa la carpeta y almacena los metadatos en la variable 'data'
    data = exporter.process_folder()
    # Carpeta de salida para el archivo de metadatos
    output_folder = "output_folder"
    # Ruta completa del archivo de metadatos que se va a generar
    outputdir = os.path.join(output_folder, "_img_metadata.csv")
    # Exporta los metadatos a un archivo en la ruta especificada
    exporter.export_data(data, outputdir)