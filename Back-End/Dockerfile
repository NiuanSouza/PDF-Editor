FROM python:3.12-slim

WORKDIR /app

# Dependências do sistema necessárias para pikepdf
RUN apt-get update && apt-get install -y --no-install-recommends \
    libqpdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python
COPY requirements/ /app/requirements/
RUN pip install --no-cache-dir -r requirements/base.txt

# Copiar o projeto
COPY . /app/

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput

# Aplicar migrações e iniciar
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
