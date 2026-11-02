# Back-End

> API REST responsável por receber arquivos do Front-End, manipular PDFs e realizar conversões com `pikepdf`, `pdf2docx`, `PyMuPDF`, `Pillow`, `ReportLab` e `LibreOffice Headless`.

## ⚙️ Arquitetura e Modelagem

O servidor segue a arquitetura **Django Apps** com uma camada dedicada de serviços isolados:

```
Back-End/
 ├── manage.py                  # Ponto de entrada CLI do Django
 ├── config/
 │    ├── settings/base.py      # Configurações globais (CORS, Whitenoise, DB)
 │    ├── urls.py               # Roteador master: /admin/, /api/, /tools/
 │    └── wsgi.py               # Interface WSGI para o Gunicorn
 ├── apps/
 │    ├── api/
 │    │    ├── views.py         # Endpoints REST para todas as operações
 │    │    ├── urls.py          # Mapeamento de rotas /api/*
 │    │    └── tests.py         # Testes automatizados cobrindo todas as ferramentas
 │    ├── audit/
 │    │    └── models.py        # Modelo AuditLog (IP, ferramenta, status, timestamp)
 │    └── pdf_tools/
 │         └── services/        # Lógica de negócio das ferramentas PDF
 │              ├── merge_service.py
 │              ├── split_service.py
 │              ├── compress_service.py
 │              ├── word_service.py
 │              ├── image_service.py
 │              ├── security_service.py
 │              └── transform_service.py
 ├── requirements/base.txt      # Dependências Python
 └── Dockerfile                 # Imagem de produção (Python 3.12-slim + LibreOffice)
```

## 🌐 Endpoints Disponíveis (`/api/`)

| Rota | Método | Descrição |
| :--- | :---: | :--- |
| `/api/merge/` | POST | Junta múltiplos PDFs |
| `/api/split/` | POST | Divide páginas em ZIP ou intervalo |
| `/api/compress/` | POST | Comprime e otimiza o PDF |
| `/api/word-to-pdf/` | POST | Converte Word (.docx/.doc) para PDF |
| `/api/pdf-to-word/` | POST | Converte PDF para Word (.docx) editável |
| `/api/pdf-to-images/` | POST | Extrai páginas em JPG/PNG |
| `/api/images-to-pdf/` | POST | Une imagens em um arquivo PDF |
| `/api/protect/` | POST | Criptografa o PDF com senha (AES-256) |
| `/api/unlock/` | POST | Remove restrições e senha do PDF |
| `/api/rotate/` | POST | Rotaciona páginas (90°, 180°, 270°) |
| `/api/watermark/` | POST | Aplica marca d'água textual |

## 🧪 Testes Automatizados

```bash
python manage.py test apps.api
```
