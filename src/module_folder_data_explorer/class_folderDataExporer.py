import os
import csv
import json
from dotenv import find_dotenv, load_dotenv

# Importa tus módulos personalizados
from module_embeddings.class_embedinnizer import Embeddings
from module_embeddings.class_embeddingDescriber import EmbeddingDescriber
from module_search_engine.class_searchEngine import GoogleSearchEngine 

class FolderDataExporter:
    def __init__(self, folder_path, output_folder='OutputFiles'):
        """
        folder_path: ruta de la carpeta a procesar.
        output_folder: carpeta donde se almacenan los archivos de salida.
        """
        self.folder_path = folder_path
        self.output_folder = output_folder
        os.makedirs(self.output_folder, exist_ok=True)
    
    def get_file_info(self, file_path):
        """
        Extrae la información básica de un archivo y crea el diccionario de metadatos.
        Se dejan campos vacíos para que luego se completen con los resultados de los modelos.
        """
        file_name = os.path.basename(file_path)
        directory = os.path.dirname(file_path)
        return {
            "file_name": file_name,
            "directory": directory,
            "embedding": "",            # Se completará con el embedding de la imagen
            "short_description": "",    # Se completará con la descripción corta
            "long_description": "",     # Se completará con la descripción larga
            "search_links": "",         # Se completará con la lista de links de búsqueda
            "output_file_directory": "",# Se completará con el directorio de salida para archivos relacionados
            "img_counts": 0             # Se completará con el número de imágenes (por ejemplo, las descargadas)
        }
    
    def process_single_image_with_models(self, image_path, embeddings, embeddingTranslator, researcher,
                                           extra_context='', theme='', search_engine='google_images'):
        """
        Procesa una sola imagen aplicando los modelos:
          - Obtiene el embedding.
          - Extrae las descripciones (corta y larga).
          - Realiza la búsqueda para obtener links.
          - Crea (si no existe) un directorio de salida y cuenta las imágenes en él.
        
        Retorna un diccionario con toda la información.
        """
        file_info = self.get_file_info(image_path)
        
        # 1. Obtener el embedding
        image_embedding = embeddings.getImgEmbedding(image_path)
        file_info['embedding'] = image_embedding.tolist() if hasattr(image_embedding, 'tolist') else image_embedding
        
        # 2. Extraer descripciones. Se asume que extractDescription retorna un diccionario con claves 'concise_description' y 'detailed_description'
        img_metadata = embeddingTranslator.extractDescription(
            image_embedding=image_embedding,
            additional_context=extra_context,
            theme=theme,
            search_engine=search_engine )
        
        file_info['short_description'] = img_metadata.get('concise_description', '')
        file_info['long_description'] = img_metadata.get('detailed_description', '')

        # 3. Realizar la búsqueda y obtener links (se espera que researcher.searchImgs retorne una lista de URLs)
        #   Esta es la linea mas importante. Aqui, se le puede decir que descripcion elegir.
        #   Actualmente elegimos la larga, pero si queremos establecer algun cambio el modleo debe de poder funcionar correctamente.
        # Para acceder a el o ver como funciona bien debes de ir al modulo:
        #     - module_search_engine.class_searchEngine -> Aqui dentro al metodo searchImgs, que es el core con las propiedades de las imagenes.
        #       - Aplicamos el metodo extract_links qu el retorna una lista de links filtrando el resto de la informacion.
        links = researcher.extract_links(file_info['short_description'], 5, "LARGE", "photo")
        file_info['search_links'] = links
        
        # 4. Definir un directorio de salida para esta imagen (por ejemplo, un subdirectorio basado en el nombre del archivo)
        subfolder = os.path.join(self.output_folder, os.path.splitext(os.path.basename(image_path))[0])
        # os.makedirs(subfolder, exist_ok=True)
        file_info['output_file_directory'] = subfolder
        
        # 5. Contar el número de imágenes en el directorio de salida
        file_info['img_counts'] = len(links)
        
        return file_info
    def export_data(self, data, output_file):
        """
        Exporta los datos al formato CSV.
        Si el archivo ya existe, se conservará la información previa y se adjuntarán las nuevas filas.
        """
        self.export_csv(data, output_file)
    
    def _ensure_output_dir(self, output_file):
        """
        Crea el directorio de salida si no existe.
        """
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
    
    def export_csv(self, data, output_file):
        """
        Exporta los datos en formato CSV.
        Si el archivo ya existe, se leen las filas existentes y se añade la nueva información,
        manteniendo todas las columnas completas.
        """
        self._ensure_output_dir(output_file)
        combined_data = []
        
        # Si el archivo ya existe, leer la información previa
        if os.path.exists(output_file):
            with open(output_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row = {k.strip(): v for k, v in row.items()}  # Limpia las claves
                    combined_data.append(row)
        
        # Añadir los nuevos datos
        combined_data.extend(data)
        
        # Se usan las claves del primer registro (ya sea de los datos existentes o de los nuevos)
        keys = combined_data[0].keys() if combined_data else data[0].keys()
        
        # Escribir todos los datos combinados en el archivo CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(combined_data)
        print(f"Datos exportados a CSV en: {output_file}")

    def update_data_range(self, embeddings, embeddingTranslator, researcher, file_range=None,
                          extra_context='', theme='', search_engine='google_images', csv_file=None):
        """
        Actualiza los metadatos de un rango específico de archivos.
        
        Args:
            embeddings, embeddingTranslator, researcher: modelos y servicios para procesar la imagen.
            file_range (tuple, optional): Rango a procesar (start, end). Si no se especifica, procesa todos.
            extra_context (str): Contexto adicional para la descripción.
            theme (str): Tema para la descripción.
            search_engine (str): Motor de búsqueda.
            csv_file (str, optional): Ruta del archivo CSV a actualizar. Si no se especifica, se usa
                                      un archivo por defecto en self.output_folder.
        
        La función realiza lo siguiente:
          1. Obtiene la lista de archivos de imagen y aplica el rango especificado.
          2. Procesa cada imagen del rango para obtener su metadata actualizada.
          3. Lee el CSV existente (si existe) y fusiona los registros, actualizando únicamente las columnas
             cuyos valores hayan cambiado.
          4. Escribe el CSV actualizado.
        """
        if csv_file is None:
            csv_file = os.path.join(self.output_folder, "_img_metadata.csv")
        
        # 1. Recopilar y ordenar los archivos de imagen
        files = []
        for root, dirs, files_list in os.walk(self.folder_path):
            for f in files_list:
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    files.append(os.path.join(root, f))
        files.sort()  # Asegura un orden estable
        
        # Aplicar el rango especificado, si se define
        if file_range:
            start, end = file_range
            files = files[start:end]
        
        # 2. Procesar cada imagen en el rango y almacenar la nueva metadata usando la ruta completa como clave
        new_data = {}
        for file_path in files:
            new_info = self.process_single_image_with_models(
                file_path, embeddings, embeddingTranslator, researcher,
                extra_context=extra_context, theme=theme, search_engine=search_engine
            )
            new_data[file_path] = new_info
        
        # 3. Leer la data existente del CSV (si existe) y almacenarla en un diccionario
        existing_data = {}
        if os.path.exists(csv_file):
            with open(csv_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Usamos la combinación de 'directory' y 'file_name' para identificar de forma única cada registro
                    row = {k.strip(): v for k, v in row.items()}  # Limpia las claves
                    key = os.path.join(row["directory"], row["file_name"])
                    existing_data[key] = row
        
        # 4. Fusionar la nueva data con la existente, actualizando solo las columnas modificadas
        for file_path, new_info in new_data.items():
            key = file_path  # La clave que usamos es la ruta completa
            if key in existing_data:
                for col, new_value in new_info.items():
                    if col == 'img_counts':
                        # Convertir el valor existente a entero (CSV lo lee como string) y sumar el nuevo conteo
                        try:
                            existing_count = int(existing_data[key].get(col, 0))
                        except ValueError:
                            existing_count = 0
                        combined_count = existing_count + int(new_value)
                        existing_data[key][col] = combined_count
                    elif col == 'search_links':
                        # Procesar search_links para concatenar nuevos links sin duplicar
                        # Intentamos interpretar el valor existente como una lista JSON, si falla, lo separamos por comas
                        try:
                            existing_links = json.loads(existing_data[key].get(col, "[]"))
                        except Exception:
                            existing_str = existing_data[key].get(col, "")
                            existing_links = [link.strip() for link in existing_str.split(",") if link.strip()] if existing_str else []
                        
                        # Aseguramos que el nuevo valor es una lista
                        if not isinstance(new_value, list):
                            try:
                                new_links = json.loads(new_value)
                            except Exception:
                                new_links = [link.strip() for link in new_value.split(",") if link.strip()]
                        else:
                            new_links = new_value
                        
                        # Agregar nuevos links que no estén ya en la lista existente
                        for link in new_links:
                            if link not in existing_links:
                                existing_links.append(link)
                        
                        # Guardamos la lista actualizada como string JSON
                        existing_data[key][col] = json.dumps(existing_links)
                    else:
                        # Actualización normal para las demás columnas
                        if new_value and new_value != existing_data[key].get(col, ""):
                            existing_data[key][col] = new_value
            else:
                # Para registros nuevos, formateamos search_links como JSON si no lo es
                if 'search_links' in new_info:
                    if not isinstance(new_info['search_links'], list):
                        try:
                            links_list = json.loads(new_info['search_links'])
                        except Exception:
                            links_list = [link.strip() for link in new_info['search_links'].split(",") if link.strip()]
                        new_info['search_links'] = json.dumps(links_list)
                    else:
                        new_info['search_links'] = json.dumps(new_info['search_links'])
                existing_data[key] = new_info
        # 5. Escribir la data fusionada en el CSV
        if existing_data:
            # Obtener el orden de columnas a partir de uno de los registros
            keys = list(next(iter(existing_data.values())).keys())
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for entry in existing_data.values():
                    writer.writerow(entry)
            print(f"Datos actualizados en: {csv_file}")