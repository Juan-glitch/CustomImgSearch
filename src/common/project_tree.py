"""
Generador de estructura de directorios para documentación.

Este script genera un árbol de directorios en formato ASCII, ideal para incluir
en la documentación de proyectos (por ejemplo, en el README.md). Permite excluir
directorios y archivos específicos mediante patrones.

Uso:
    python project_tree.py [--output README.md] [--ignore-dirs .git,venv] [--ignore-files *.pyc,*.tmp]

Ejemplos:
    1. Mostrar árbol en consola:
       python project_tree.py

    2. Guardar en README.md e ignorar archivos .log y .tmp:
       python project_tree.py --output README.md --ignore-files "*.log,*.tmp"

    3. Ignorar directorios específicos:
       python project_tree.py --ignore-dirs ".git,venv,temp"
"""

import os
import argparse
import fnmatch

def generate_project_tree(start_path, ignore_dirs=[], ignore_files=[], output_file=None):
    """
    Genera un árbol de directorios en formato ASCII apto para Markdown.

    Args:
        start_path (str): Ruta inicial del proyecto.
        ignore_dirs (list): Lista de directorios a ignorar.
        ignore_files (list): Lista de patrones de archivos a ignorar (soporta wildcards).
        output_file (str, optional): Archivo de salida. Si se proporciona, guarda el árbol
                                    en el archivo especificado. Por defecto es None.

    Returns:
        None: Imprime el árbol en consola o lo guarda en el archivo especificado.
    """
    tree = ["```\n"]
    
    def should_ignore(name, is_dir):
        """
        Determina si un archivo o directorio debe ser ignorado.

        Args:
            name (str): Nombre del archivo o directorio.
            is_dir (bool): True si es un directorio, False si es un archivo.

        Returns:
            bool: True si debe ser ignorado, False en caso contrario.
        """
        if is_dir:
            return name in ignore_dirs
        else:
            return any(fnmatch.fnmatch(name, pattern) for pattern in ignore_files)

    def build_tree(path, prefix='', is_last=True):
        """
        Construye recursivamente el árbol de directorios.

        Args:
            path (str): Ruta actual.
            prefix (str): Prefijo para la indentación.
            is_last (bool): Indica si es el último elemento en su directorio padre.
        """
        name = os.path.basename(path)
        line = f"{prefix}└── {name}" if is_last else f"{prefix}├── {name}"
        
        if prefix == "":
            tree.append(f"{name}\n")
        else:
            tree.append(f"{line}\n")
            
        if os.path.isdir(path):
            new_prefix = prefix + ("    " if is_last else "│   ")
            
            try:
                items = sorted(os.listdir(path))
                items = [item for item in items if not should_ignore(item, os.path.isdir(os.path.join(path, item)))]
            except PermissionError:
                return

            dirs = [d for d in items if os.path.isdir(os.path.join(path, d))]
            files = [f for f in items if not os.path.isdir(os.path.join(path, f))]
            sorted_items = dirs + files

            for index, item in enumerate(sorted_items):
                is_last_item = index == len(sorted_items) - 1
                build_tree(os.path.join(path, item), new_prefix, is_last_item)

    build_tree(start_path)
    tree.append("```")
    
    result = "".join(tree)
    
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"## Estructura del proyecto\n\n{result}\n")
        print(f"✓ Árbol generado en {output_file}")
    else:
        print(result)

if __name__ == "__main__":
    # Directorios y archivos ignorados por defecto
    DEFAULT_IGNORE_DIRS = [".git", "__pycache__", "venv", ".pytest_cache"]
    DEFAULT_IGNORE_FILES = ["*.pyc", "*.tmp", "*.log"]

    # Configuración del parser de argumentos
    parser = argparse.ArgumentParser(
        description="Genera un árbol de directorios en formato ASCII para documentación.",
        epilog="Ejemplo: python project_tree.py --output README.md --ignore-dirs .git,venv"
    )
    parser.add_argument(
        "--output",
        help="Archivo de salida (ej. README.md)",
        default=None
    )
    parser.add_argument(
        "--ignore-dirs",
        help="Directorios a ignorar (separados por comas)",
        default=",".join(DEFAULT_IGNORE_DIRS)
    )
    parser.add_argument(
        "--ignore-files",
        help="Patrones de archivos a ignorar (separados por comas, soporta wildcards)",
        default=",".join(DEFAULT_IGNORE_FILES)
    )
    
    args = parser.parse_args()
    
    # Procesar listas de ignorados
    ignore_dirs = [item.strip() for item in args.ignore_dirs.split(",")]
    ignore_files = [item.strip() for item in args.ignore_files.split(",")]
    
    # Generar el árbol
    generate_project_tree(
        start_path=os.getcwd(),
        ignore_dirs=ignore_dirs,
        ignore_files=ignore_files,
        output_file=args.output
    )