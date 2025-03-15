import os
import csv
import json
import pandas as pd

class CSVDataNavigator:
    """
    Clase para navegar y acceder a los archivos de salida generados por FolderDataExporter.
    Permite cargar, filtrar, buscar y exportar información de los archivos CSV generados.
    """
    
    def __init__(self, csv_file_path):
        """
        Inicializa el navegador con la ruta al archivo CSV generado por FolderDataExporter.
        
        Args:
            csv_file_path (str): Ruta al archivo CSV con los metadatos de las imágenes.
        """
        self.csv_file_path = csv_file_path
        self.data = None
        self.load_data()
    
    def load_data(self):
        """
        Carga los datos del archivo CSV en un DataFrame de pandas para facilitar
        su manipulación y consulta.
        """
        if not os.path.exists(self.csv_file_path):
            raise FileNotFoundError(f"El archivo CSV no existe en la ruta: {self.csv_file_path}")
        
        self.data = pd.read_csv(self.csv_file_path)
        
        # Procesar columnas especiales (como listas JSON)
        if 'search_links' in self.data.columns:
            self.data['search_links'] = self.data['search_links'].apply(
                lambda x: json.loads(x) if isinstance(x, str) and x.strip().startswith('[') else 
                          (x.split(',') if isinstance(x, str) else [])
            )
        
        print(f"Datos cargados. Total de registros: {len(self.data)}")
    
    def get_image_info(self, file_name=None, index=None):
        """
        Obtiene la información de una imagen específica por nombre de archivo o índice.
        
        Args:
            file_name (str, optional): Nombre del archivo de imagen a buscar.
            index (int, optional): Índice en el DataFrame (útil para iteración).
            
        Returns:
            dict: Información completa de la imagen o None si no se encuentra.
        """
        if file_name is not None:
            result = self.data[self.data['file_name'] == file_name]
            if not result.empty:
                return result.iloc[0].to_dict()
            return None
        
        if index is not None and 0 <= index < len(self.data):
            return self.data.iloc[index].to_dict()
        
        return None
    
    def get_row_properties(self, index_or_filename, properties=None):
        """
        Extrae propiedades específicas de una fila del CSV de manera estructurada y fácil de usar.
        
        Args:
            index_or_filename: Puede ser un índice numérico o el nombre del archivo de imagen.
            properties (list, optional): Lista de propiedades específicas a extraer. 
                                        Si es None, extrae todas las propiedades disponibles.
        
        Returns:
            dict: Diccionario con las propiedades estructuradas de manera accesible.
                  Retorna None si la fila no existe.
        
        Ejemplo:
            # Obtener directory, file_name y search_links de la primera fila
            props = navigator.get_row_properties(0, ['directory', 'file_name', 'search_links'])
            
            # Acceder a las propiedades
            print(f"Directorio: {props['directory']}")
            print(f"Archivo: {props['file_name']}")
            print(f"Enlaces: {props['search_links']}")
        """
        # Determinar si es un índice o un nombre de archivo
        if isinstance(index_or_filename, int):
            if 0 <= index_or_filename < len(self.data):
                row = self.data.iloc[index_or_filename]
            else:
                return None
        else:
            result = self.data[self.data['file_name'] == index_or_filename]
            if result.empty:
                return None
            row = result.iloc[0]
        
        # Extraer propiedades solicitadas o todas si no se especifican
        if properties is None:
            properties = row.index.tolist()
        
        result_dict = {}
        for prop in properties:
            if prop in row.index:
                value = row[prop]
                
                # Procesamiento especial para ciertos tipos de datos
                if prop == 'embedding' and isinstance(value, str):
                    try:
                        value = json.loads(value)
                    except:
                        pass
                
                result_dict[prop] = value
        
        # Añadir propiedades derivadas útiles
        if 'directory' in result_dict and 'file_name' in result_dict:
            result_dict['full_path'] = os.path.join(result_dict['directory'], result_dict['file_name'])
        
        return result_dict
    
    def filter_by_description(self, query, field='long_description'):
        """
        Filtra imágenes cuya descripción contenga la consulta especificada.
        
        Args:
            query (str): Texto a buscar en las descripciones.
            field (str): Campo donde buscar ('short_description' o 'long_description').
            
        Returns:
            pd.DataFrame: DataFrame filtrado con las coincidencias.
        """
        if field not in ['short_description', 'long_description']:
            raise ValueError("El campo debe ser 'short_description' o 'long_description'")
        
        return self.data[self.data[field].str.contains(query, case=False, na=False)]
    
    def get_image_paths(self, filtered_df=None):
        """
        Obtiene las rutas completas de las imágenes, opcionalmente de un DataFrame filtrado.
        
        Args:
            filtered_df (pd.DataFrame, optional): DataFrame filtrado del cual obtener las rutas.
            
        Returns:
            list: Lista de rutas completas a las imágenes.
        """
        df = filtered_df if filtered_df is not None else self.data
        return [os.path.join(row['directory'], row['file_name']) for _, row in df.iterrows()]
    
    def get_search_links(self, file_name=None, index=None):
        """
        Obtiene los enlaces de búsqueda asociados a una imagen específica.
        
        Args:
            file_name (str, optional): Nombre del archivo de imagen.
            index (int, optional): Índice en el DataFrame.
            
        Returns:
            list: Lista de enlaces o lista vacía si no se encuentra.
        """
        image_info = self.get_image_info(file_name, index)
        if image_info and 'search_links' in image_info:
            return image_info['search_links']
        return []
    
    def export_filtered_data(self, filtered_df, output_path):
        """
        Exporta un DataFrame filtrado a un nuevo archivo CSV.
        
        Args:
            filtered_df (pd.DataFrame): DataFrame filtrado a exportar.
            output_path (str): Ruta de salida para el nuevo archivo CSV.
        """
        # Asegurarse de que la columna search_links esté en formato serializado para CSV
        if 'search_links' in filtered_df.columns:
            filtered_df = filtered_df.copy()
            filtered_df['search_links'] = filtered_df['search_links'].apply(
                lambda x: json.dumps(x) if isinstance(x, list) else x
            )
        
        filtered_df.to_csv(output_path, index=False)
        print(f"Datos filtrados exportados a: {output_path}")
    
    def group_by_directory(self):
        """
        Agrupa las imágenes por directorio.
        
        Returns:
            dict: Diccionario con directorios como claves y listas de nombres de archivo como valores.
        """
        grouped = {}
        for _, row in self.data.iterrows():
            directory = row['directory']
            if directory not in grouped:
                grouped[directory] = []
            grouped[directory].append(row['file_name'])
        
        return grouped
    
    def get_images_with_similar_descriptions(self, target_image_name, threshold=0.7):
        """
        Encuentra imágenes con descripciones similares a la imagen objetivo
        usando la similitud de texto simple.
        
        Args:
            target_image_name (str): Nombre del archivo de imagen objetivo.
            threshold (float): Umbral de similitud (0-1).
            
        Returns:
            pd.DataFrame: DataFrame con las imágenes similares.
        """
        from difflib import SequenceMatcher
        
        target_info = self.get_image_info(target_image_name)
        if not target_info:
            return pd.DataFrame()
        
        target_desc = target_info.get('long_description', '')
        
        def get_similarity(desc):
            if not desc or not target_desc:
                return 0
            return SequenceMatcher(None, desc, target_desc).ratio()
        
        self.data['similarity'] = self.data['long_description'].apply(get_similarity)
        similar_images = self.data[self.data['similarity'] >= threshold]
        
        # Ordenar por similitud descendente
        return similar_images.sort_values(by='similarity', ascending=False)
    
    def get_all_output_directories(self):
        """
        Obtiene todos los directorios de salida únicos definidos en los metadatos.
        
        Returns:
            list: Lista de directorios de salida únicos.
        """
        if 'output_file_directory' in self.data.columns:
            return self.data['output_file_directory'].unique().tolist()
        return []
    
    def summary_stats(self):
        """
        Genera estadísticas resumidas del conjunto de datos.
        
        Returns:
            dict: Diccionario con estadísticas sobre los datos.
        """
        stats = {
            'total_images': len(self.data),
            'unique_directories': len(self.data['directory'].unique()),
            'avg_links_per_image': self.data['img_counts'].mean(),
            'images_without_links': sum(self.data['img_counts'] == 0),
            'most_common_words': self._get_common_words()
        }
        return stats
    
    def _get_common_words(self, field='short_description', top_n=10):
        """
        Método auxiliar para encontrar las palabras más comunes en las descripciones.
        
        Args:
            field (str): Campo a analizar.
            top_n (int): Número de palabras más comunes a devolver.
            
        Returns:
            dict: Diccionario con las palabras más comunes y sus frecuencias.
        """
        if field not in self.data.columns:
            return {}
        
        from collections import Counter
        import re
        
        all_text = ' '.join(self.data[field].dropna())
        words = re.findall(r'\w+', all_text.lower())
        
        # Filtrar palabras comunes (stopwords)
        stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'of'}
        filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
        
        return dict(Counter(filtered_words).most_common(top_n))