#!/bin/bash
set -x  # Activar la depuración

# Tu script aquí
# Load environment variables from the .env file inside /app
if [ -f /app/.env ]; then
    # Filtrar las líneas que no contienen comentarios ni están vacías y exportarlas
    export $(grep -v '^\s*#' /app/.env | grep -v '^\s*$' | sed 's/#.*//g' | xargs)
fi

# Verificar si las variables fueron exportadas correctamente
echo "GIT_USER_NAME: $GIT_USER_NAME"
echo "GIT_USER_EMAIL: $GIT_USER_EMAIL"

# Set Git user name and email from .env
git config --global user.name "$GIT_USER_NAME"
git config --global user.email "$GIT_USER_EMAIL"
