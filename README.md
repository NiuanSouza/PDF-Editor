# PDF Editor Pro

> Uma ferramenta web gratuita e open-source para manipulação de PDFs diretamente no navegador. Sem cadastro, sem limite, sem complicação.

## 🚀 Visão Geral

O **PDF Editor Pro** permite que qualquer usuário:

- **Juntar PDFs**: Combine múltiplos arquivos em um único PDF, na ordem que quiser, com drag & drop
- **Dark Mode nativo**: Alterna automaticamente com a preferência do sistema ou manualmente
- **Zero instalação para o usuário**: Tudo roda no navegador, o processamento pesado fica no servidor

A arquitetura separa completamente a interface (Front-End estático) da lógica de negócio (Back-End Django), permitindo escalar cada parte de forma independente.

## 📂 Estrutura do Repositório

- **/Front-End**: Interface de usuário em HTML5, CSS3 e Vanilla JS com Drag & Drop e Dark Mode. [Veja o README do Front-End](./Front-End/README.md)
- **/Back-End**: API REST em Django 5+ que recebe os PDFs, realiza o merge com `pikepdf` e retorna o arquivo mesclado para download. [Veja o README do Back-End](./Back-End/README.md)

## 🛠 Como executar o projeto

```bash
# 1. Suba o Back-End
cd Back-End
pip install -r requirements/base.txt
python manage.py migrate
python manage.py runserver
# API disponível em http://localhost:8000

# 2. Sirva o Front-End (em outro terminal)
cd Front-End
python3 -m http.server 3000
# Interface disponível em http://localhost:3000/merge.html
```

> ⚠️ Use um servidor local para o Front-End (não abra o `.html` direto). O `type="module"` do JavaScript exige protocolo `http://`.
