# Version: 0.0.1 | Updated: 2025-03-17 15:06:30 | Branch: DEV | Commit: c6cc354 |  Repo: Juan-glitch/CustomImgSearch
"""
Generador de documentacion para clases Python.

Uso:
    python doc_generator.py <nombre_script> [--output <documentacion.md>]
O ejecucion directa con valores predeterminados.
"""
import os
import ast
from typing import List, Dict, Any

class ClassAnalyzer(ast.NodeVisitor):

    def __init__(self):
        """
        Description:
             __init__ function.
        Args:
        """
        self.classes = []
        self.current_class = None

    def visit_ClassDef(self, node: ast.ClassDef):
        """
        Description:
             visit_ClassDef function.
        Args:
            node: The first parameter.
        Returns:
            None
        """
        class_info = {'name': node.name, 'docstring': ast.get_docstring(node), 'methods': [], 'inherits': [base.id for base in node.bases if isinstance(base, ast.Name)]}
        self.current_class = class_info
        self.classes.append(class_info)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        Description:
             visit_FunctionDef function.
        Args:
            node: The first parameter.
        Returns:
            None
        """
        if self.current_class is None:
            return
        args = []
        for arg in node.args.args:
            arg_info = {'name': arg.arg, 'type': ast.unparse(arg.annotation) if arg.annotation else None, 'default': None}
            args.append(arg_info)
        returns = ast.unparse(node.returns) if node.returns else None
        method_info = {'name': node.name, 'docstring': ast.get_docstring(node), 'args': args, 'returns': returns, 'decorators': [ast.unparse(decorator) for decorator in node.decorator_list]}
        self.current_class['methods'].append(method_info)

def find_file_in_project_root(file_name: str) -> str:
    """
    Description:
         find_file_in_project_root function.
    Args:
        file_name: The first parameter.
    Returns:
        The return value. TODO: Describe return value.
    """
    project_root = os.getcwd()
    for root, _, files in os.walk(project_root):
        for file in files:
            if file == f'{file_name}.py':
                return os.path.join(root, file)
    raise FileNotFoundError(f"Archivo '{file_name}.py' no encontrado en el proyecto.")

def analyze_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Description:
         analyze_file function.
    Args:
        file_path: The first parameter.
    Returns:
        The return value. TODO: Describe return value.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
    analyzer = ClassAnalyzer()
    analyzer.visit(tree)
    return analyzer.classes

def generate_markdown_template(classes: List[Dict[str, Any]]) -> str:
    """
    Description:
         generate_markdown_template function.
    Args:
        classes: The first parameter.
    Returns:
        The return value. TODO: Describe return value.
    """
    markdown = '# Documentacion de Clases\n\n'
    for class_info in classes:
        class_header = f"## Clase `{class_info['name']}`\n"
        if class_info['inherits']:
            class_header += f"*Herencia: {', '.join(class_info['inherits'])}*\n"
        class_description = f"### Descripcion General\n{class_info['docstring'] or '> [TODO: Agregar descripcion de la clase]'}\n\n"
        methods_section = '### Metodos\n'
        methods_table = '| Metodo | Descripcion | Parametros | Retorno |\n|--------|-------------|------------|---------|\n'
        for method in class_info['methods']:
            params = '<br>'.join([f"`{arg['name']}`" + (f": {arg['type']}" if arg['type'] else '') + (f" = {arg['default']}" if arg['default'] else '') for arg in method['args']])
            returns = f"`{method['returns']}`" if method['returns'] else 'None'
            methods_table += f"| `{method['name']}` | {(method['docstring'].splitlines()[0] if method['docstring'] else '[TODO: Agregar descripcion]')} | {params} | {returns} |\n"
        example_section = '\n### Ejemplo de Uso\n```python\n# [TODO: Agregar ejemplo de uso]\n```\n'
        markdown += f'{class_header}\n{class_description}{methods_section}{methods_table}\n{example_section}\n'
    return markdown

def main(file_name: str='example', use_argparse: bool=True):
    """
    Description:
         main function.
    Args:
        file_name: The first parameter.
        use_argparse: The second parameter.
    Returns:
        None
    """
    output_file = None
    if use_argparse:
        import argparse
        parser = argparse.ArgumentParser(description='Generador de documentacion para clases Python')
        parser.add_argument('file', help='Nombre del archivo Python (sin .py)')
        args = parser.parse_args()
        file_name = args.file
    try:
        file_path = find_file_in_project_root(file_name)
        output_dir = os.path.dirname(file_path)
        output_file = os.path.join(output_dir, 'DOCUMENTACION.md')
        classes = analyze_file(file_path)
        documentation = generate_markdown_template(classes)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(documentation)
        print(f'✓ Documentacion generada en {output_file}')
    except FileNotFoundError as e:
        print(f'Error: {str(e)}')
    except Exception as e:
        print(f'Error inesperado: {str(e)}')
if __name__ == '__main__':
    main(file_name='class_embedinnizer', use_argparse=False)
