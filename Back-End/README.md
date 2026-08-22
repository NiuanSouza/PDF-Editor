# Back-End

> API REST responsável por receber arquivos PDF do Front-End, realizar o merge com `pikepdf` e retornar o arquivo mesclado para download imediato.

## ⚙️ Arquitetura e Modelagem

O servidor segue a arquitetura **Django Apps** — cada domínio de negócio é isolado em seu próprio app:

```
Back-End/
 ├── manage.py                  # Ponto de entrada CLI do Django
 ├── config/
 │    ├── settings/base.py      # Configurações globais (CORS, Whitenoise, DB)
 │    ├── urls.py               # Roteador master: /admin/, /api/, /tools/
 │    └── wsgi.py               # Interface WSGI para o Gunicorn
 ├── apps/
 │    ├── api/
 │    │    ├── views.py         # POST /api/merge/ — lógica de merge com pikepdf
 │    │    └── urls.py          # Rotas da API REST
 │    ├── audit/
 │    │    └── models.py        # Modelo AuditLog (IP, ferramenta, status, timestamp)
 │    └── pdf_tools/            # App reservado para futuras ferramentas (split, compress)
 ├── requirements/base.txt      # Dependências Python
 ├── Dockerfile                 # Imagem de produção (Python 3.12-slim)
 └── render.yaml                # Configuração de deploy no Render.com
```

**Banco de dados**: SQLite por padrão (sem configuração necessária). Suporta PostgreSQL via variável `DATABASE_URL`.

**Fluxo de uma requisição de merge**:
1. Front-End envia `POST /api/merge/` com os PDFs em `multipart/form-data`
2. `api/views.py` valida os arquivos, abre cada PDF com `pikepdf` e une as páginas
3. Salva um registro em `AuditLog` com IP, quantidade de arquivos e status
4. Retorna o PDF mesclado como download (`Content-Disposition: attachment`)

## 🛠 Tecnologias Usadas

- **Python 3.12 + Django 5** — framework principal e construção das rotas REST
- **pikepdf** — manipulação e merge de PDFs em memória (sem salvar no disco)
- **Gunicorn** — servidor WSGI de produção
- **Whitenoise** — serve arquivos estáticos sem precisar de Nginx separado
- **django-cors-headers** — permite chamadas cross-origin do Front-End
- **SQLite** — banco de dados para logs de auditoria (zero configuração)

## 🚀 Como Rodar o Back-End

### Opção 1 — Desenvolvimento local (Python direto)

```bash
# 1. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env se necessário (o padrão já funciona para dev)

# 2. Instale as dependências
pip install -r requirements/base.txt

# 3. Aplique as migrações
python manage.py migrate

# 4. Inicie o servidor
python manage.py runserver
# API disponível em http://localhost:8000
```

### Opção 2 — Docker

```bash
# Build e execução
docker build -t pdf-editor-backend .
docker run -p 8000:8000 pdf-editor-backend
```

### Deploy no Render.com

1. Conecte o repositório (pasta `Back-End` como Root Directory)
2. **Build Command**: `pip install -r requirements/base.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput`
3. **Start Command**: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2`
4. **Variáveis de ambiente** (em Settings → Environment):

| Variável | Valor |
|---|---|
| `SECRET_KEY` | Gere com o botão "Generate" |
| `DEBUG` | `False` |
| `DJANGO_SETTINGS_MODULE` | `config.settings.base` |
| `ALLOWED_HOSTS` | `*` |
| `CORS_ALLOW_ALL_ORIGINS` | `True` |

### Testando a API de merge

```bash
curl -X POST http://localhost:8000/api/merge/ \
  -F "files=@arquivo1.pdf" \
  -F "files=@arquivo2.pdf" \
  --output merged.pdf
```
