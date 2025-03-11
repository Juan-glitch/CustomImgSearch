#!/bin/bash
set -x  # Activar la depuración

# Verificar que el archivo .env esté presente
if [ -f /app/.env ]; then
    echo "Contenido de .env:"
    cat /app/.env

    # Filtrar y exportar variables del archivo .env
    while IFS='=' read -r key value; do
        # Eliminar los espacios al principio y final de las claves y los valores
        key=$(echo $key | xargs)
        value=$(echo $value | xargs)

        # Asegurarse de que las variables no estén vacías
        if [ -n "$key" ] && [ -n "$value" ]; then
            export "$key"="$value"
        fi
    done < /app/.env
fi

# Verificar si las variables fueron exportadas correctamente
echo "GIT_USER_NAME: $GIT_USER_NAME"
echo "GIT_USER_EMAIL: $GIT_USER_EMAIL"

# Set Git user name and email globally
git config --global user.name "$GIT_USER_NAME"
git config --global user.email "$GIT_USER_EMAIL"

# Set Git user name and email locally (in the current repository)
git config user.name "$GIT_USER_NAME"
git config user.email "$GIT_USER_EMAIL"

# Verificar que se hayan configurado correctamente
echo "Configuración global:"
git config --global user.name
git config --global user.email

echo "Configuración local (repositorio actual):"
git config user.name
git config user.email
