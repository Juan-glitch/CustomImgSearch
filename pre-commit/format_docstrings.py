# Version: 0.0.1 | Updated: 2025-03-17 15:06:31 | Branch: DEV | Commit: c6cc354 |  Repo: Juan-glitch/CustomImgSearch
"""
Docstring & Signature Formatter en estilo Google con logging, modo recursivo y opciones para pre-commit.
Este script analiza archivos Python y actualiza (o inserta) las docstrings de las funciones/métodos,
asegurando que sigan el siguiente formato (con la indentación correcta):

    def download_image(url, dest_path):
        '''
        Description:
            download_image function.
        Args:
            url: The first parameter.
            dest_path: The second parameter.
        Returns:
            None
        '''
        # código de la función…

Adicionalmente, si la línea de definición es muy larga se rompe en varias líneas.
"""
import ast
import sys
import os
import logging
import argparse
import re
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

def ordinal_str(n: int) -> str:
    """
    Description:
         ordinal_str function.
    Args:
        n: The first parameter.
    Returns:
        The return value. TODO: Describe return value.
    """
    mapping = {1: 'first', 2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth', 6: 'sixth', 7: 'seventh', 8: 'eighth', 9: 'ninth', 10: 'tenth'}
    return mapping.get(n, f'{n}th')

def generate_docstring(func: ast.FunctionDef, col_offset: int) -> str:
    """
    Description:
         generate_docstring function.
    Args:
        func: The first parameter.
        col_offset: The second parameter.
    Returns:
        The return value. TODO: Describe return value.
    """
    base_indent = ' ' * (col_offset + 4)
    desc_content_indent = ' ' * (col_offset + 9)
    item_indent = ' ' * (col_offset + 8)
    lines = []
    lines.append('')
    lines.append(f'{base_indent}Description:')
    lines.append(f'{desc_content_indent}{func.name} function.')
    lines.append(f'{base_indent}Args:')
    args_list = func.args.args
    if args_list and args_list[0].arg == 'self':
        args_list = args_list[1:]
    for i, arg in enumerate(args_list, start=1):
        lines.append(f'{item_indent}{arg.arg}: The {ordinal_str(i)} parameter.')
    if func.name != '__init__':
        ret_text = 'None' if func.returns is None or (isinstance(func.returns, ast.Constant) and func.returns.value is None) else 'The return value. TODO: Describe return value.'
        lines.append(f'{base_indent}Returns:')
        lines.append(f'{item_indent}{ret_text}')
    lines.append('')
    return '\n'.join(lines)

def reformat_function_definitions(code: str, max_width: int=80) -> str:
    """
    Description:
         reformat_function_definitions function.
    Args:
        code: The first parameter.
        max_width: The second parameter.
    Returns:
        The return value. TODO: Describe return value.
    """

    def replacer(match):
        """
        Description:
             replacer function.
        Args:
            match: The first parameter.
        Returns:
            None
        """
        line = match.group(0)
        try:
            start = line.index('(')
            end = line.rindex('):')
        except ValueError:
            return line
        signature_start = line[:start + 1]
        signature_end = '):'
        params_str = line[start + 1:end]
        params = [p.strip() for p in params_str.split(',') if p.strip()]
        indent_match = re.match('^(\\s*)def ', line)
        base_indent = indent_match.group(1) if indent_match else ''
        subsequent_indent = ' ' * len(signature_start)
        new_lines = []
        current_line = signature_start
        for token in params:
            token += ', '
            if len(current_line) + len(token) > max_width and current_line != signature_start:
                new_lines.append(current_line.rstrip())
                current_line = subsequent_indent + token
            else:
                current_line += token
        new_lines.append(current_line.rstrip(', '))
        new_lines[-1] = new_lines[-1] + signature_end
        return '\n'.join(new_lines)
    pattern = re.compile('^\\s*def\\s+\\w+\\(.*\\):$', re.MULTILINE)
    return pattern.sub(replacer, code)

def fix_docstring_closing(code: str) -> str:
    """
    Description:
         fix_docstring_closing function.
    Args:
        code: The first parameter.
    Returns:
        The return value. TODO: Describe return value.
    """
    pattern = re.compile('^(?P<indent>[ \\t]*)("""\\n)(?P<content>.*?)(?P<closing>""")', re.DOTALL | re.MULTILINE)

    def replacer(match):
        """
        Description:
             replacer function.
        Args:
            match: The first parameter.
        Returns:
            None
        """
        indent = match.group('indent')
        opening = match.group(2)
        content = match.group('content').rstrip()
        closing = match.group('closing')
        return f'{indent}{opening}{content}\n{indent}{closing}'
    return pattern.sub(replacer, code)

class DocstringTransformer(ast.NodeTransformer):
    """
    Recorre el árbol AST e inserta o actualiza la docstring de cada función/método.
    """

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        Description:
             visit_FunctionDef function.
        Args:
            node: The first parameter.
        Returns:
            None
        """
        self.generic_visit(node)
        new_doc = generate_docstring(node, node.col_offset)
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, (ast.Str, ast.Constant)):
            logging.info(f'Actualizando docstring en función: {node.name}')
            node.body[0].value = ast.Constant(value=new_doc)
        else:
            logging.info(f'Insertando nueva docstring en función: {node.name}')
            doc_node = ast.Expr(value=ast.Constant(value=new_doc))
            node.body.insert(0, doc_node)
        return node

def format_file(file_path: str) -> None:
    """
    Description:
         format_file function.
    Args:
        file_path: The first parameter.
    Returns:
        None
    """
    logging.info(f'Procesando archivo: {file_path}')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        logging.error(f'Error al leer {file_path}: {e}')
        return
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        logging.error(f'Error de sintaxis en {file_path}: {e}')
        return
    transformer = DocstringTransformer()
    new_tree = transformer.visit(tree)
    try:
        new_code = ast.unparse(new_tree)
    except Exception as e:
        logging.error(f'Error al generar el nuevo código para {file_path}: {e}')
        return
    new_code = reformat_function_definitions(new_code, max_width=80)
    new_code = fix_docstring_closing(new_code)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_code)
        logging.info(f'Archivo formateado exitosamente: {file_path}')
    except Exception as e:
        logging.error(f'Error al escribir en {file_path}: {e}')

def get_python_files(root_dir: str) -> list:
    """
    Description:
         get_python_files function.
    Args:
        root_dir: The first parameter.
    Returns:
        The return value. TODO: Describe return value.
    """
    python_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.py'):
                full_path = os.path.join(dirpath, filename)
                python_files.append(full_path)
    return python_files

def main():
    """
    Description:
         main function.
    Args:
    Returns:
        None
    """
    parser = argparse.ArgumentParser(description='Formateador de docstrings y firmas de funciones en estilo Google, con logs y modo recursivo.')
    parser.add_argument('files', nargs='*', help='Archivos Python a formatear (compatible con pre-commit).')
    parser.add_argument('--all', action='store_true', help='Procesar recursivamente todos los archivos .py desde el directorio raíz.')
    parser.add_argument('--root', default='.', help='Directorio raíz para buscar archivos (usado con --all). Por defecto es el directorio actual.')
    args = parser.parse_args()
    files_to_process = []
    if args.all:
        logging.info(f'Modo --all activado. Se buscarán archivos en: {args.root}')
        files_to_process = get_python_files(args.root)
        if not files_to_process:
            logging.warning('No se encontraron archivos .py en el directorio especificado.')
    elif args.files:
        files_to_process = args.files
    else:
        logging.error('No se especificaron archivos y no se activó el modo --all.')
        sys.exit(1)
    for file_path in files_to_process:
        format_file(file_path)
if __name__ == '__main__':
    main()
