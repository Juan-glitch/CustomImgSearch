# Version: 0.0.1 | Updated: 2025-03-17 15:06:31 | Branch: DEV | Commit: c6cc354 |  Repo: Juan-glitch/CustomImgSearch
import os
import csv
import json
from dotenv import find_dotenv, load_dotenv
from module_embeddings.class_embedinnizer import Embeddings
from module_embeddings.class_embeddingDescriber import EmbeddingDescriber
from module_search_engine.class_searchEngine import GoogleSearchEngine

class FolderDataExporter:

    def __init__(self, folder_path, output_folder,
                  output_csv_path='OutputFiles'):
        """
        Description:
             __init__ function.
        Args:
            folder_path: The first parameter.
            output_folder: The second parameter.
            output_csv_path: The third parameter.
        """
        self.folder_path = folder_path
        self.output_folder = output_folder
        self.output_csv_path = output_csv_path
        os.makedirs(self.output_folder, exist_ok=True)

    def get_file_info(self, file_path=''):
        """
        Description:
             get_file_info function.
        Args:
            file_path: The first parameter.
        Returns:
            None
        """
        if file_path == '':
            file_path = self.output_folder
        file_name = os.path.basename(file_path)
        directory = os.path.dirname(file_path)
        return {'file_name': file_name, 'directory': directory, 'embedding': '', 'short_description': '', 'long_description': '', 'search_links': '', 'output_file_directory': '', 'img_counts': 0}

    def process_directory(self, directory_path=None, output_csv_path=None):
        """
        Description:
             process_directory function.
        Args:
            directory_path: The first parameter.
            output_csv_path: The second parameter.
        Returns:
            None
        """
        directory_path = directory_path or self.folder_path
        output_csv_path = output_csv_path or self.output_csv_path
        file_data = []
        for root, _, files in os.walk(directory_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                file_info = self.get_file_info(file_path)
                file_data.append(file_info)
        with open(output_csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=['file_name', 'directory', 'embedding', 'short_description', 'long_description', 'search_links', 'output_file_directory', 'img_counts'])
            writer.writeheader()
            writer.writerows(file_data)
        print(f'Datos guardados en {output_csv_path}')

    def process_single_image_with_models(self, image_path, embeddings,
                                          embeddingTranslator, researcher,
                                          extra_context='', theme='',
                                          search_engine='google_images'):
        """
        Description:
             process_single_image_with_models function.
        Args:
            image_path: The first parameter.
            embeddings: The second parameter.
            embeddingTranslator: The third parameter.
            researcher: The fourth parameter.
            extra_context: The fifth parameter.
            theme: The sixth parameter.
            search_engine: The seventh parameter.
        Returns:
            None
        """
        file_info = self.get_file_info(image_path)
        image_embedding = embeddings.getImgEmbedding(image_path)
        file_info['embedding'] = image_embedding.tolist() if hasattr(image_embedding, 'tolist') else image_embedding
        img_metadata = embeddingTranslator.extractDescription(image_embedding=image_embedding, additional_context=extra_context, theme=theme, search_engine=search_engine)
        file_info['short_description'] = img_metadata.get('concise_description', '')
        file_info['long_description'] = img_metadata.get('detailed_description', '')
        links = researcher.extract_links(file_info['short_description'], 5, 'LARGE', 'photo')
        file_info['search_links'] = links
        subfolder = os.path.join(self.output_folder, os.path.splitext(os.path.basename(image_path))[0])
        file_info['output_file_directory'] = subfolder
        file_info['img_counts'] = len(links)
        return file_info

    def export_data(self, data, output_file):
        """
        Description:
             export_data function.
        Args:
            data: The first parameter.
            output_file: The second parameter.
        Returns:
            None
        """
        self.export_csv(data, output_file)

    def _ensure_output_dir(self, output_file):
        """
        Description:
             _ensure_output_dir function.
        Args:
            output_file: The first parameter.
        Returns:
            None
        """
        output_dir = os.path.dirname(output_file)
        if output_dir and (not os.path.exists(output_dir)):
            os.makedirs(output_dir, exist_ok=True)

    def export_csv(self, data, output_file):
        """
        Description:
             export_csv function.
        Args:
            data: The first parameter.
            output_file: The second parameter.
        Returns:
            None
        """
        self._ensure_output_dir(output_file)
        combined_data = []
        if os.path.exists(output_file):
            with open(output_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row = {k.strip(): v for k, v in row.items()}
                    combined_data.append(row)
        combined_data.extend(data)
        keys = combined_data[0].keys() if combined_data else data[0].keys()
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(combined_data)
        print(f'Datos exportados a CSV en: {output_file}')

    def update_data_range(self, embeddings, embeddingTranslator, researcher,
                           file_range=None, extra_context='', theme='',
                           search_engine='google_images', csv_file=None):
        """
        Description:
             update_data_range function.
        Args:
            embeddings: The first parameter.
            embeddingTranslator: The second parameter.
            researcher: The third parameter.
            file_range: The fourth parameter.
            extra_context: The fifth parameter.
            theme: The sixth parameter.
            search_engine: The seventh parameter.
            csv_file: The eighth parameter.
        Returns:
            None
        """
        if csv_file is None:
            csv_file = os.path.join(self.output_folder, '_img_metadata.csv')
        files = []
        for root, dirs, files_list in os.walk(self.folder_path):
            for f in files_list:
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    files.append(os.path.join(root, f))
        files.sort()
        if file_range:
            start, end = file_range
            files = files[start:end]
        new_data = {}
        for file_path in files:
            new_info = self.process_single_image_with_models(file_path, embeddings, embeddingTranslator, researcher, extra_context=extra_context, theme=theme, search_engine=search_engine)
            new_data[file_path] = new_info
        existing_data = {}
        if os.path.exists(csv_file):
            with open(csv_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row = {k.strip(): v for k, v in row.items()}
                    key = os.path.join(row['directory'], row['file_name'])
                    existing_data[key] = row
        for file_path, new_info in new_data.items():
            key = file_path
            if key in existing_data:
                for col, new_value in new_info.items():
                    if col == 'img_counts':
                        try:
                            existing_count = int(existing_data[key].get(col, 0))
                        except ValueError:
                            existing_count = 0
                        combined_count = existing_count + int(new_value)
                        existing_data[key][col] = combined_count
                    elif col == 'search_links':
                        try:
                            existing_links = json.loads(existing_data[key].get(col, '[]'))
                        except Exception:
                            existing_str = existing_data[key].get(col, '')
                            existing_links = [link.strip() for link in existing_str.split(',') if link.strip()] if existing_str else []
                        if not isinstance(new_value, list):
                            try:
                                new_links = json.loads(new_value)
                            except Exception:
                                new_links = [link.strip() for link in new_value.split(',') if link.strip()]
                        else:
                            new_links = new_value
                        for link in new_links:
                            if link not in existing_links:
                                existing_links.append(link)
                        existing_data[key][col] = json.dumps(existing_links)
                    elif new_value and new_value != existing_data[key].get(col, ''):
                        existing_data[key][col] = new_value
            else:
                if 'search_links' in new_info:
                    if not isinstance(new_info['search_links'], list):
                        try:
                            links_list = json.loads(new_info['search_links'])
                        except Exception:
                            links_list = [link.strip() for link in new_info['search_links'].split(',') if link.strip()]
                        new_info['search_links'] = json.dumps(links_list)
                    else:
                        new_info['search_links'] = json.dumps(new_info['search_links'])
                existing_data[key] = new_info
        if existing_data:
            keys = list(next(iter(existing_data.values())).keys())
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for entry in existing_data.values():
                    writer.writerow(entry)
            print(f'Datos actualizados en: {csv_file}')