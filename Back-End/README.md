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
 └── Dockerfile                 # Imagem de produção (Python 3.12-slim)
```

**Banco de dados**: SQLite por padrão (sem configuração necessária).

**Fluxo de uma requisição de merge**:
1. Front-End envia `POST /api/merge/` com os PDFs em `multipart/form-data`
2. `api/views.py` valida os arquivos, abre cada PDF com `pikepdf` e une as páginas em memória
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

### Execução local

```bash
# 1. Instale as dependências
pip install -r requirements/base.txt

# 2. Aplique as migrações
python manage.py migrate

# 3. Inicie o servidor
python manage.py runserver
# API disponível em http://localhost:8000
```

### Via Docker

```bash
docker build -t pdf-editor-backend .
docker run -p 8000:8000 pdf-editor-backend
```

### Testando a API de merge

```bash
curl -X POST http://localhost:8000/api/merge/ \
  -F "files=@arquivo1.pdf" \
  -F "files=@arquivo2.pdf" \
  --output merged.pdf
```
