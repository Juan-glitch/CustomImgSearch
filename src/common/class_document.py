"""
Generador de documentación para clases Python

Uso:
    python doc_generator.py <nombre_script> [--output <documentacion.md>]
O ejecución directa con valores predeterminados.
"""
import os
import ast
from typing import List, Dict, Any


class ClassAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.classes = []
        self.current_class = None

    def visit_ClassDef(self, node: ast.ClassDef):
        """Procesa la definición de clases y extrae su información."""
        class_info = {
            'name': node.name,
            'docstring': ast.get_docstring(node),
            'methods': [],
            'inherits': [base.id for base in node.bases if isinstance(base, ast.Name)]
        }
        self.current_class = class_info
        self.classes.append(class_info)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Procesa los métodos de las clases."""
        if self.current_class is None:
            return

        args = []
        for arg in node.args.args:
            arg_info = {
                'name': arg.arg,
                'type': ast.unparse(arg.annotation) if arg.annotation else None,
                'default': None
            }
            args.append(arg_info)

        returns = ast.unparse(node.returns) if node.returns else None

        method_info = {
            'name': node.name,
            'docstring': ast.get_docstring(node),
            'args': args,
            'returns': returns,
            'decorators': [ast.unparse(decorator) for decorator in node.decorator_list]
        }
        self.current_class['methods'].append(method_info)


def find_file_in_project_root(file_name: str) -> str:
    """Busca un archivo en la raíz del proyecto."""
    project_root = os.getcwd()  # Cambiar según sea necesario
    for root, _, files in os.walk(project_root):
        for file in files:
            if file == f"{file_name}.py":
                return os.path.join(root, file)
    raise FileNotFoundError(f"Archivo '{file_name}.py' no encontrado en el proyecto.")


def analyze_file(file_path: str) -> List[Dict[str, Any]]:
    """Analiza un archivo Python y devuelve una lista de clases con sus métodos."""
    with open(file_path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())

    analyzer = ClassAnalyzer()
    analyzer.visit(tree)
    return analyzer.classes


def generate_markdown_template(classes: List[Dict[str, Any]]) -> str:
    """Genera una plantilla en Markdown para documentar las clases."""
    markdown = "# Documentación de Clases\n\n"

    for class_info in classes:
        class_header = f"## Clase `{class_info['name']}`\n"
        if class_info['inherits']:
            class_header += f"*Herencia: {', '.join(class_info['inherits'])}*\n"

        class_description = (
            "### Descripción General\n"
            f"{class_info['docstring'] or '> [TODO: Agregar descripción de la clase]'}\n\n"
        )

        methods_section = "### Métodos\n"
        methods_table = (
            "| Método | Descripción | Parámetros | Retorno |\n"
            "|--------|-------------|------------|---------|\n"
        )

        for method in class_info['methods']:
            params = "<br>".join([
                f"`{arg['name']}`" +
                (f": {arg['type']}" if arg['type'] else "") +
                (f" = {arg['default']}" if arg['default'] else "")
                for arg in method['args']
            ])

            returns = f"`{method['returns']}`" if method['returns'] else "None"

            methods_table += (
                f"| `{method['name']}` | "
                f"{method['docstring'].splitlines()[0] if method['docstring'] else '[TODO: Agregar descripción]'} | "
                f"{params} | "
                f"{returns} |\n"
            )

        example_section = (
            "\n### Ejemplo de Uso\n"
            "```python\n"
            "# [TODO: Agregar ejemplo de uso]\n"
            "```\n"
        )

        markdown += (
            f"{class_header}\n"
            f"{class_description}"
            f"{methods_section}{methods_table}\n"
            f"{example_section}\n"
        )

    return markdown


def main(file_name: str = "example", use_argparse: bool = True):
    """Ejecuta el script con o sin argparse."""
    output_file = None

    if use_argparse:
        import argparse
        parser = argparse.ArgumentParser(description="Generador de documentación para clases Python")
        parser.add_argument("file", help="Nombre del archivo Python (sin .py)")
        args = parser.parse_args()
        file_name = args.file

    try:
        # Buscar el archivo en la raíz del proyecto
        file_path = find_file_in_project_root(file_name)

        # Determinar la ruta del archivo de salida en el mismo directorio del archivo encontrado
        output_dir = os.path.dirname(file_path)
        output_file = os.path.join(output_dir, "DOCUMENTACION.md")

        # Analizar el archivo y generar documentación
        classes = analyze_file(file_path)
        documentation = generate_markdown_template(classes)

        # Guardar el archivo de documentación
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(documentation)

        print(f"✓ Documentación generada en {output_file}")
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")


# Ejecución directa sin argparse
if __name__ == "__main__":
    main(file_name="class_embedinnizer", use_argparse=False)
