import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from module_folder_data_explorer.class_folderDataExporer import FolderDataExporter

# Ejemplo de uso:
if __name__ == '__main__':
        # Definir las rutas al inicio para mayor claridad
    OUTPUT_FOLDER = "output_folder"
    METADATA_FILE = os.path.join(OUTPUT_FOLDER, "_img_metadata.csv")
    FOLDER_PATH = "Imagenes_Panes"
    

    # Instancia del exportador de datos, especificando el formato de salida (csv, json o yml)
    exporter = FolderDataExporter(FOLDER_PATH, OUTPUT_FOLDER, METADATA_FILE)  
    exporter.process_directory()

