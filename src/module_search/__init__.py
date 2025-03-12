import os
import sys

# Agrega automáticamente la ruta base del proyecto al sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))  # Obtén la ruta actual
project_root = os.path.abspath(os.path.join(current_dir, ".."))  # Ruta del proyecto raíz
sys.path.append(project_root)

# Imprime las rutas para depuración (opcional)
print("Rutas en sys.path:")
print("\n".join(sys.path))
