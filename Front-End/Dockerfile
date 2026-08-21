FROM nginx:1.25-alpine

# Remover a configuração padrão do Nginx (se necessário para costumizações)
RUN rm -rf /usr/share/nginx/html/*

# Copiar os arquivos estáticos do FrontEnd para o diretório padrão do Nginx
COPY . /usr/share/nginx/html/

EXPOSE 80
