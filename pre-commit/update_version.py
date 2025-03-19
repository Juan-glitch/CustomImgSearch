#!/usr/bin/env python3
"""
Script para actualizar automáticamente la información de versión y referencias de GitHub en archivos.
Puede ser utilizado como un hook de pre-commit.

Uso:
    python update_version.py [--staged | --pre-staged | --all] [--dir DIRECTORY] [--extensions ext1,ext2,...]
"""

import os
import re
import subprocess
import argparse
import datetime
import hashlib
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("version_update.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("version_updater")

def get_git_branch():
    """Obtiene la rama actual de git."""
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            universal_newlines=True
        ).strip()
        return branch
    except subprocess.SubprocessError as e:
        logger.warning(f"No se pudo obtener la rama git: {str(e)}")
        return "unknown-branch"

def get_git_commit_hash():
    """Obtiene el hash del último commit de git."""
    try:
        commit_hash = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            universal_newlines=True
        ).strip()
        return commit_hash
    except subprocess.SubprocessError as e:
        logger.warning(f"No se pudo obtener el hash del commit: {str(e)}")
        return "unknown-commit"

def get_git_remote_url():
    """Obtiene la URL remota del repositorio git."""
    try:
        remote_url = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            universal_newlines=True
        ).strip()
        return remote_url
    except subprocess.SubprocessError as e:
        logger.warning(f"No se pudo obtener la URL remota: {str(e)}")
        return "unknown-remote"

def get_comment_style(file_path):
    """
    Determina el estilo de comentario adecuado según la extensión del archivo.

    Args:
        file_path: Ruta al archivo

    Returns:
        dict: Diccionario con información sobre el estilo de comentario
    """
    ext = os.path.splitext(file_path)[1].lower().lstrip('.')
    filename = os.path.basename(file_path).lower()

    # Definir estilos de comentario por extensión
    comment_styles = {
        # Scripts y lenguajes con # para comentarios
        'py': {'line': '#', 'block_start': '"""', 'block_end': '"""'},
        'rb': {'line': '#', 'block_start': '=begin', 'block_end': '=end'},
        'pl': {'line': '#', 'block_start': '=pod', 'block_end': '=cut'},
        'sh': {'line': '#', 'block_start': ': <<\'EOC\'', 'block_end': 'EOC'},
        'bash': {'line': '#', 'block_start': ': <<\'EOC\'', 'block_end': 'EOC'},
        'zsh': {'line': '#', 'block_start': ': <<\'EOC\'', 'block_end': 'EOC'},
        'yaml': {'line': '#', 'block_start': None, 'block_end': None},
        'yml': {'line': '#', 'block_start': None, 'block_end': None},

        # Lenguajes con // para comentarios
        'js': {'line': '//', 'block_start': '/*', 'block_end': '*/'},
        'ts': {'line': '//', 'block_start': '/*', 'block_end': '*/'},
        'jsx': {'line': '//', 'block_start': '/*', 'block_end': '*/'},
        'tsx': {'line': '//', 'block_start': '/*', 'block_end': '*/'},
        'java': {'line': '//', 'block_start': '/*', 'block_end': '*/'},
        'c': {'line': '//', 'block_start': '/*', 'block_end': '*/'},
        'cpp': {'line': '//', 'block_start': '/*', 'block_end': '*/'},
        'h': {'line': '//', 'block_start': '/*', 'block_end': '*/'},
        'hpp': {'line': '//', 'block_start': '/*', 'block_end': '*/'},
        'cs': {'line': '//', 'block_start': '/*', 'block_end': '*/'},
        'go': {'line': '//', 'block_start': '/*', 'block_end': '*/'},
        'php': {'line': '//', 'block_start': '/*', 'block_end': '*/'},
        'swift': {'line': '//', 'block_start': '/*', 'block_end': '*/'},
        'kt': {'line': '//', 'block_start': '/*', 'block_end': '*/'},
        'rs': {'line': '//', 'block_start': '/*', 'block_end': '*/'},
        'scala': {'line': '//', 'block_start': '/*', 'block_end': '*/'},
        'dart': {'line': '//', 'block_start': '/*', 'block_end': '*/'},

        # Lenguajes de marcado y XML
        'html': {'line': None, 'block_start': '<!--', 'block_end': '-->'},
        'xml': {'line': None, 'block_start': '<!--', 'block_end': '-->'},
        'svg': {'line': None, 'block_start': '<!--', 'block_end': '-->'},
        'md': {'line': None, 'block_start': '<!--', 'block_end': '-->'},
        'markdown': {'line': None, 'block_start': '<!--', 'block_end': '-->'},
        'handlebars': {'line': None, 'block_start': '<!--', 'block_end': '-->'},
        'hbs': {'line': None, 'block_start': '<!--', 'block_end': '-->'},

        # CSS y variantes
        'css': {'line': None, 'block_start': '/*', 'block_end': '*/'},
        'scss': {'line': '//', 'block_start': '/*', 'block_end': '*/'},
        'sass': {'line': '//', 'block_start': '/*', 'block_end': '*/'},
        'less': {'line': '//', 'block_start': '/*', 'block_end': '*/'},

        # SQL y variantes
        'sql': {'line': '--', 'block_start': '/*', 'block_end': '*/'},

        # Lenguajes funcionales
        'hs': {'line': '--', 'block_start': '{-', 'block_end': '-}'},
        'lhs': {'line': '--', 'block_start': '{-', 'block_end': '-}'},
        'elm': {'line': '--', 'block_start': '{-', 'block_end': '-}'},
        'lisp': {'line': ';;', 'block_start': '#|', 'block_end': '|#'},
        'clj': {'line': ';;', 'block_start': '#_', 'block_end': None},

        # Lenguajes especializados
        'r': {'line': '#', 'block_start': None, 'block_end': None},
        'tex': {'line': '%', 'block_start': None, 'block_end': None},
        'latex': {'line': '%', 'block_start': None, 'block_end': None},
        'bat': {'line': 'REM', 'block_start': None, 'block_end': None},
        'ps1': {'line': '#', 'block_start': '<#', 'block_end': '#>'},

        # Archivos de configuración
        'ini': {'line': ';', 'block_start': None, 'block_end': None},
        'conf': {'line': '#', 'block_start': None, 'block_end': None},
        'cfg': {'line': '#', 'block_start': None, 'block_end': None},
    }

    # Casos especiales por nombre de archivo
    if filename in ['.gitignore', '.dockerignore', 'makefile', 'dockerfile']:
        return {'line': '#', 'block_start': None, 'block_end': None}

    # Caso especial para JSON - No soporta comentarios en el estándar,
    # pero algunos procesadores permiten comentarios estilo JS
    if ext == 'json':
        return {'line': '//', 'block_start': '/*', 'block_end': '*/', 'json': True}

    # Devolver el estilo adecuado o un estilo por defecto
    return comment_styles.get(ext, {'line': '#', 'block_start': None, 'block_end': None})

def get_modified_files(mode="staged"):
    """
    Obtiene la lista de archivos modificados según el modo especificado.

    Args:
        mode: 'staged', 'pre-staged' o 'all'

    Returns:
        Lista de rutas de archivos modificados
    """
    try:
        if mode == "staged":
            # Archivos en el área de staging
            files = subprocess.check_output(
                ["git", "diff", "--name-only", "--cached"],
                universal_newlines=True
            ).splitlines()
        elif mode == "pre-staged":
            # Archivos modificados pero no en staging
            files = subprocess.check_output(
                ["git", "diff", "--name-only"],
                universal_newlines=True
            ).splitlines()
        elif mode == "all":
            # Todos los archivos modificados (staging + no staging)
            staged = subprocess.check_output(
                ["git", "diff", "--name-only", "--cached"],
                universal_newlines=True
            ).splitlines()

            unstaged = subprocess.check_output(
                ["git", "diff", "--name-only"],
                universal_newlines=True
            ).splitlines()

            # También incluir archivos no rastreados
            untracked = subprocess.check_output(
                ["git", "ls-files", "--others", "--exclude-standard"],
                universal_newlines=True
            ).splitlines()

            files = list(set(staged + unstaged + untracked))
        else:
            files = []

        return files
    except subprocess.SubprocessError as e:
        logger.error(f"Error al obtener archivos modificados: {str(e)}")
        return []

def filter_files(files, directory=None, extensions=None):
    """
    Filtra archivos por directorio y extensiones.

    Args:
        files: Lista de rutas de archivos
        directory: Directorio para filtrar (opcional)
        extensions: Lista de extensiones para filtrar (opcional)

    Returns:
        Lista filtrada de rutas de archivos
    """
    result = []

    for file in files:
        # Verificar si el archivo existe
        if not os.path.isfile(file):
            continue

        # Filtrar por directorio
        if directory and not file.startswith(directory):
            continue

        # Filtrar por extensión
        if extensions:
            ext = os.path.splitext(file)[1].lstrip('.')
            if ext not in extensions:
                continue

        result.append(file)

    return result

def handle_json_file(file_path):
    """
    Maneja archivos JSON de forma especial.

    Args:
        file_path: Ruta al archivo JSON

    Returns:
        tuple: (éxito, contenido actualizado o None)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()

        # Obtener información de git
        branch = get_git_branch()
        commit = get_git_commit_hash()
        remote = get_git_remote_url()

        # Formatear URL remota
        if "github.com" in remote:
            if remote.startswith("git@github.com:"):
                repo_info = remote.split('git@github.com:')[1].replace('.git', '')
            elif remote.startswith("https://github.com/"):
                repo_info = remote.split('https://github.com/')[1].replace('.git', '')
            else:
                repo_info = remote
        else:
            repo_info = remote

        # Información para la actualización
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Si el archivo ya tiene un campo de versión, actualizarlo
        import json
        try:
            json_data = json.loads(content)

            # Verificar si es un diccionario
            if isinstance(json_data, dict):
                # Actualizar versión si existe
                if "version" in json_data:
                    # Extraer componentes de la versión
                    version_parts = json_data["version"].split('.')
                    if len(version_parts) >= 3:
                        major, minor, patch = map(int, version_parts[:3])
                        patch += 1
                        json_data["version"] = f"{major}.{minor}.{patch}"
                    else:
                        # Si no tiene formato semántico, agregar .1
                        json_data["version"] = f"{json_data['version']}.1"
                else:
                    # Agregar versión si no existe
                    json_data["version"] = "0.0.1"

                # Agregar información de actualización
                json_data["_meta"] = {
                    "lastUpdate": now,
                    "branch": branch,
                    "commit": commit,
                    "repository": repo_info
                }

                # Convertir de vuelta a JSON con indentación
                updated_content = json.dumps(json_data, indent=2)
                return True, updated_content
        except json.JSONDecodeError:
            logger.warning(f"El archivo {file_path} no es un JSON válido, tratando como texto plano")

        # Si falló el enfoque JSON, tratar como texto plano
        return False, None

    except Exception as e:
        logger.error(f"Error al procesar archivo JSON {file_path}: {str(e)}")
        return False, None

def update_version_info(file_path):
    """
    Actualiza la información de versión en un archivo.

    Args:
        file_path: Ruta al archivo que se va a actualizar

    Returns:
        boolean: True si se actualizó el archivo, False en caso contrario
    """
    try:
        # Verificar el tipo de archivo para manejo especial
        ext = os.path.splitext(file_path)[1].lower().lstrip('.')

        # Manejo especial para JSON
        if ext == 'json':
            success, updated_content = handle_json_file(file_path)
            if success and updated_content:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(updated_content)
                return True

        # Para otros tipos de archivo, continuar con el enfoque normal
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Calcular el hash del contenido actual para detectar cambios posteriores
        original_hash = hashlib.md5(content.encode()).hexdigest()

        # Obtener información de git
        branch = get_git_branch()
        commit = get_git_commit_hash()
        remote = get_git_remote_url()

        # Formatear URL remota para mostrar solo la parte relevante
        if "github.com" in remote:
            # Extraer usuario/repo de la URL de GitHub
            if remote.startswith("git@github.com:"):
                repo_info = remote.split('git@github.com:')[1].replace('.git', '')
            elif remote.startswith("https://github.com/"):
                repo_info = remote.split('https://github.com/')[1].replace('.git', '')
            else:
                repo_info = remote
        else:
            repo_info = remote

        # Información para la actualización
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        update_info = f"Updated: {now} | Branch: {branch} | Commit: {commit} | Repo: {repo_info}"

        # Patrón para buscar información de versión existente
        version_pattern = re.compile(r'Version: (\d+)\.(\d+)\.(\d+)')
        update_pattern = re.compile(r'Updated: .*?\|.*?\|.*?\|')

        modified_content = content

        # Actualizar/agregar versión
        version_match = version_pattern.search(content)
        if version_match:
            major, minor, patch = map(int, version_match.groups())
            patch += 1  # Incrementar versión de ajuste
            new_version = f"Version: {major}.{minor}.{patch}"
            modified_content = version_pattern.sub(new_version, modified_content)
        else:
            # Si no existe información de versión, agregarla al principio del archivo
            new_version = "Version: 0.0.1"

            # Obtener el estilo de comentario adecuado para este tipo de archivo
            comment_style = get_comment_style(file_path)

            # Detectar si es un archivo binario
            try:
                content.encode('ascii')
                is_binary = False
            except UnicodeEncodeError:
                # Si contiene caracteres no ASCII, verificar si parece ser un archivo de texto
                if '\0' in content[:1024]:
                    logger.info(f"Saltando archivo binario: {file_path}")
                    return False
                is_binary = False

            if is_binary:
                logger.info(f"Saltando archivo binario: {file_path}")
                return False

            # Preparar la línea de información con el estilo de comentario adecuado
            if comment_style.get('line'):
                # Usar comentario de línea
                comment_start = comment_style['line'] + ' '
                comment_end = ''
            elif comment_style.get('block_start'):
                # Usar comentario de bloque
                comment_start = comment_style['block_start'] + ' '
                comment_end = ' ' + comment_style['block_end']
            else:
                # Sin estilo de comentario reconocido
                comment_start = '# '
                comment_end = ''

            version_line = f"{comment_start}{new_version} | {update_info}{comment_end}"

            # Buscar la posición adecuada para insertar
            lines = modified_content.split('\n')
            insert_position = 0

            # Buscar líneas especiales al inicio
            for i, line in enumerate(lines):
                # Ignorar shebang en la primera línea si existe
                if i == 0 and line.startswith('#!'):
                    insert_position = 1
                    continue

                # Ignorar líneas en blanco
                if not line.strip():
                    insert_position = i + 1
                    continue

                # Si encuentra una línea de comentario, seguir avanzando
                if (line.strip().startswith('#') or
                    line.strip().startswith('//') or
                    line.strip().startswith('/*') or
                    line.strip().startswith('*') or
                    line.strip().startswith('<!--') or
                    line.strip().startswith('--') or
                    line.strip().startswith(';') or
                    line.strip().startswith('%')):
                    insert_position = i + 1
                else:
                    break

            # Insertar la línea de versión
            lines.insert(insert_position, version_line)
            modified_content = '\n'.join(lines)

        # Actualizar información de actualización si ya existe
        if update_pattern.search(modified_content):
            modified_content = update_pattern.sub(f"Updated: {now} | Branch: {branch} | Commit: {commit} | ", modified_content)

        # Verificar si hubo cambios
        new_hash = hashlib.md5(modified_content.encode()).hexdigest()
        if original_hash == new_hash:
            return False

        # Escribir el contenido modificado al archivo
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)

        return True
    except Exception as e:
        logger.error(f"Error al actualizar {file_path}: {str(e)}")
        return False

def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(description="Actualiza información de versión y referencias de GitHub en archivos.")

    # Argumentos para el modo de selección de archivos
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--staged", action="store_true", help="Actualizar solo archivos en staging")
    group.add_argument("--pre-staged", action="store_true", help="Actualizar solo archivos modificados pero no en staging")
    group.add_argument("--all", action="store_true", help="Actualizar todos los archivos modificados")

    # Argumentos para filtrado
    parser.add_argument("--dir", help="Directorio para filtrar archivos")
    parser.add_argument("--extensions", help="Extensiones de archivo para filtrar (separadas por comas)")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        default="INFO", help="Nivel de logging")

    args = parser.parse_args()

    # Configurar nivel de logging
    logger.setLevel(getattr(logging, args.log_level))

    # Determinar el modo de selección de archivos
    if args.pre_staged:
        mode = "pre-staged"
    elif args.all:
        mode = "all"
    else:
        # Por defecto, usar archivos en staging
        mode = "staged"

    logger.info(f"Iniciando actualización de versiones en modo: {mode}")

    # Obtener archivos modificados
    files = get_modified_files(mode)
    logger.info(f"Archivos modificados encontrados: {len(files)}")

    # Filtrar archivos según los argumentos
    extensions = args.extensions.split(',') if args.extensions else None
    filtered_files = filter_files(files, args.dir, extensions)
    logger.info(f"Archivos filtrados para procesar: {len(filtered_files)}")

    # Actualizar información de versión en archivos filtrados
    updated_count = 0
    error_count = 0
    error_files = []

    for file in filtered_files:
        try:
            if update_version_info(file):
                logger.info(f"Actualizado: {file}")
                updated_count += 1

                # Si estamos en modo pre-staged o all, agregar el archivo actualizado al área de staging
                if mode in ["pre-staged", "all"]:
                    try:
                        subprocess.run(["git", "add", file], check=True)
                        logger.debug(f"Archivo agregado al staging: {file}")
                    except subprocess.SubprocessError as e:
                        logger.error(f"Error al agregar {file} al área de staging: {str(e)}")
                        error_count += 1
                        error_files.append(file)
        except Exception as e:
            logger.error(f"Error procesando archivo {file}: {str(e)}")
            error_count += 1
            error_files.append(file)

    # Resumen final
    logger.info(f"Resumen de ejecución:")
    logger.info(f"- Total de archivos procesados: {len(filtered_files)}")
    logger.info(f"- Archivos actualizados correctamente: {updated_count}")
    logger.info(f"- Archivos con errores: {error_count}")

    if error_count > 0:
        logger.error("Archivos con errores:")
        for error_file in error_files:
            logger.error(f"- {error_file}")

    return 0 if error_count == 0 else 1

if __name__ == "__main__":
    exit(main())
