#!/bin/sh
set -e

# O Docker Compose (através do depends_on: condition: service_healthy)
# já garante que o banco de dados estará pronto. 
# Não precisamos mais do 'nc' (netcat) aqui.

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting application..."
exec "$@"
