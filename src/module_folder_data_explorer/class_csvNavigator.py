# Version: 0.0.1 | Updated: 2025-03-17 15:06:32 | Branch: DEV | Commit: c6cc354 |  Repo: Juan-glitch/CustomImgSearch
import os
import csv
import json
import pandas as pd

class CSVDataNavigator:
    """
    Clase para navegar y acceder a los archivos de salida generados por
    FolderDataExporter.

    Permite cargar, filtrar, buscar y exportar informacion de los
    archivos CSV generados.
    """

    def __init__(self, csv_file_path):
        """
        Description:
             __init__ function.
        Args:
            csv_file_path: The first parameter.
        """
        self.csv_file_path = csv_file_path
        self.data = None
        self.load_data()

    def load_data(self):
        """
        Description:
             load_data function.
        Args:
        Returns:
            None
        """
        if not os.path.exists(self.csv_file_path):
            raise FileNotFoundError(f'El archivo CSV no existe en la ruta: {self.csv_file_path}')
        self.data = pd.read_csv(self.csv_file_path)
        if 'search_links' in self.data.columns:
            self.data['search_links'] = self.data['search_links'].apply(lambda x: json.loads(x) if isinstance(x, str) and x.strip().startswith('[') else x.split(',') if isinstance(x, str) else [])
        print(f'Datos cargados. Total de registros: {len(self.data)}')

    def get_image_info(self, file_name=None, index=None):
        """
        Description:
             get_image_info function.
        Args:
            file_name: The first parameter.
            index: The second parameter.
        Returns:
            None
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
        Description:
             get_row_properties function.
        Args:
            index_or_filename: The first parameter.
            properties: The second parameter.
        Returns:
            None
        """
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
        if properties is None:
            properties = row.index.tolist()
        result_dict = {}
        for prop in properties:
            if prop in row.index:
                value = row[prop]
                if prop == 'embedding' and isinstance(value, str):
                    try:
                        value = json.loads(value)
                    except:
                        pass
                result_dict[prop] = value
        if 'directory' in result_dict and 'file_name' in result_dict:
            result_dict['full_path'] = os.path.join(result_dict['directory'], result_dict['file_name'])
        return result_dict

    def filter_by_description(self, query, field='long_description'):
        """
        Description:
             filter_by_description function.
        Args:
            query: The first parameter.
            field: The second parameter.
        Returns:
            None
        """
        if field not in ['short_description', 'long_description']:
            raise ValueError("El campo debe ser 'short_description' o 'long_description'")
        return self.data[self.data[field].str.contains(query, case=False, na=False)]

    def get_image_paths(self, filtered_df=None):
        """
        Description:
             get_image_paths function.
        Args:
            filtered_df: The first parameter.
        Returns:
            None
        """
        df = filtered_df if filtered_df is not None else self.data
        return [os.path.join(row['directory'], row['file_name']) for _, row in df.iterrows()]

    def get_search_links(self, file_name=None, index=None):
        """
        Description:
             get_search_links function.
        Args:
            file_name: The first parameter.
            index: The second parameter.
        Returns:
            None
        """
        image_info = self.get_image_info(file_name, index)
        if image_info and 'search_links' in image_info:
            return image_info['search_links']
        return []

    def export_filtered_data(self, filtered_df, output_path):
        """
        Description:
             export_filtered_data function.
        Args:
            filtered_df: The first parameter.
            output_path: The second parameter.
        Returns:
            None
        """
        if 'search_links' in filtered_df.columns:
            filtered_df = filtered_df.copy()
            filtered_df['search_links'] = filtered_df['search_links'].apply(lambda x: json.dumps(x) if isinstance(x, list) else x)
        filtered_df.to_csv(output_path, index=False)
        print(f'Datos filtrados exportados a: {output_path}')

    def group_by_directory(self):
        """
        Description:
             group_by_directory function.
        Args:
        Returns:
            None
        """
        grouped = {}
        for _, row in self.data.iterrows():
            directory = row['directory']
            if directory not in grouped:
                grouped[directory] = []
            grouped[directory].append(row['file_name'])
        return grouped

    def get_images_with_similar_descriptions(self, target_image_name,
                                              threshold=0.7):
        """
        Description:
             get_images_with_similar_descriptions function.
        Args:
            target_image_name: The first parameter.
            threshold: The second parameter.
        Returns:
            None
        """
        from difflib import SequenceMatcher
        target_info = self.get_image_info(target_image_name)
        if not target_info:
            return pd.DataFrame()
        target_desc = target_info.get('long_description', '')

        def get_similarity(desc):
            """
            Description:
                 get_similarity function.
            Args:
                desc: The first parameter.
            Returns:
                None
            """
            if not desc or not target_desc:
                return 0
            return SequenceMatcher(None, desc, target_desc).ratio()
        self.data['similarity'] = self.data['long_description'].apply(get_similarity)
        similar_images = self.data[self.data['similarity'] >= threshold]
        return similar_images.sort_values(by='similarity', ascending=False)

    def get_all_output_directories(self):
        """
        Description:
             get_all_output_directories function.
        Args:
        Returns:
            None
        """
        if 'output_file_directory' in self.data.columns:
            return self.data['output_file_directory'].unique().tolist()
        return []

    def summary_stats(self):
        """
        Description:
             summary_stats function.
        Args:
        Returns:
            None
        """
        stats = {'total_images': len(self.data), 'unique_directories': len(self.data['directory'].unique()), 'avg_links_per_image': self.data['img_counts'].mean(), 'images_without_links': sum(self.data['img_counts'] == 0), 'most_common_words': self._get_common_words()}
        return stats

    def _get_common_words(self, field='short_description', top_n=10):
        """
        Description:
             _get_common_words function.
        Args:
            field: The first parameter.
            top_n: The second parameter.
        Returns:
            None
        """
        if field not in self.data.columns:
            return {}
        from collections import Counter
        import re
        all_text = ' '.join(self.data[field].dropna())
        words = re.findall('\\w+', all_text.lower())
        stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'of'}
        filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
        return dict(Counter(filtered_words).most_common(top_n))