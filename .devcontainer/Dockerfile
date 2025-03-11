# Usamos una imagen base de Python 3.12 con una versión ligera de Debian (slim)
FROM python:3.12-slim

# Instalamos Git y Bash, necesarios para algunas extensiones de VS Code
RUN apt-get update && apt-get install -y git bash && apt-get clean

# Verificamos que Git está correctamente instalado
RUN git --version

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Inicializamos un repositorio Git básico para hacer feliz a la extensión GitLens de VS Code
RUN git config --global init.defaultBranch main \
    && git config --global user.email "dev@example.com" \
    && git config --global user.name "Dev Environment"  # Configuramos el usuario y correo de Git

# Copiamos la carpeta 'scripts' desde el sistema local al contenedor
COPY ./scripts /app/scripts

# Actualizamos pip (el gestor de paquetes de Python)
RUN pip install --upgrade pip

# Instalamos herramientas básicas de Python como pylint y pytest
RUN pip install pylint pytest

# Damos permisos de ejecución al script setup_git_config.sh
RUN chmod +x /app/scripts/setup_git_config.sh

# Ejecutamos el script que configura las variables de Git
RUN /app/scripts/setup_git_config.sh

# Configuramos Bash para que guarde el historial de comandos ejecutados dentro del contenedor
RUN touch /root/.bash_history && \
    chmod 666 /root/.bash_history && \
    echo 'HISTFILE=/root/.bash_history' >> /root/.bashrc && \
    echo 'HISTSIZE=10000' >> /root/.bashrc && \
    echo 'HISTFILESIZE=10000' >> /root/.bashrc

# Aseguramos que cada vez que se cierre una sesión de Bash, el historial se guarde correctamente
RUN echo 'PROMPT_COMMAND="history -a; history -n"' >> /root/.bashrc
