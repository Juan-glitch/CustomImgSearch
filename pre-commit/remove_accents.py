# Version: 0.0.1 | Updated: 2025-03-17 15:06:32 | Branch: DEV | Commit: c6cc354 |  Repo: Juan-glitch/CustomImgSearch
import os
import re

def remove_accents(text):
    """
    Description:
         remove_accents function.
    Args:
        text: The first parameter.
    Returns:
        None
    """
    accents = {'a': 'a', 'e': 'e', 'i': 'i', 'o': 'o', 'u': 'u', 'A': 'A', 'E': 'E', 'I': 'I', 'O': 'O', 'U': 'U'}
    for accented_char, non_accented_char in accents.items():
        text = re.sub(accented_char, non_accented_char, text)
    return text

def process_python_files(directory):
    """
    Description:
         process_python_files function.
    Args:
        directory: The first parameter.
    Returns:
        None
    """
    modified_files = []
    unmodified_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                new_content = remove_accents(content)
                if new_content != content:
                    modified_files.append(file_path)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                else:
                    unmodified_files.append(file_path)
    return (modified_files, unmodified_files)
modified_files, unmodified_files = process_python_files('.')
print('Se han eliminado todas las tildes de los siguientes archivos Python:')
for file in modified_files:
    print(file)
print('\nNo se encontraron tildes en los siguientes archivos Python:')
for file in unmodified_files:
    print(file)
'Nuevo docstring'
