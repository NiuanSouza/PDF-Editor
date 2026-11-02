# PDF Editor Pro

> Uma suíte web gratuita e open-source para manipulação e conversão de documentos PDF diretamente no navegador. Sem cadastro, sem limite, sem complicação.

**🔗 Acesse a ferramenta em produção:** [https://niuansouza.duckdns.org/pdf-editor/](https://niuansouza.duckdns.org/pdf-editor/)

## 🚀 Visão Geral e Funcionalidades

O **PDF Editor Pro** oferece ferramentas completas para produtividade com documentos:

### 📑 Organizar
- **Juntar PDF**: Combine múltiplos arquivos em um único PDF, na ordem que quiser com drag & drop.
- **Dividir PDF**: Separe cada página em arquivos individuais (ZIP) ou extraia intervalos customizados (ex: `1-3, 5`).
- **Rotacionar PDF**: Gire documentos em 90°, 180° ou 270° (todas as páginas, pares ou ímpares).

### 🔄 Conversão
- **Word para PDF**: Converta documentos DOCX, DOC, ODT e RTF para PDF com layout e fontes preservadas via LibreOffice Headless.
- **PDF para Word**: Converta PDFs para arquivos Word (.docx) editáveis com extração precisa de parágrafos e tabelas via `pdf2docx`.
- **PDF para Imagens**: Renderize páginas de PDFs em alta definição (JPG ou PNG em 150/300 DPI).
- **Imagens para PDF**: Una fotos e imagens JPG, PNG ou WEBP em um único PDF ordenado.

### 🛡️ Otimização & Segurança
- **Comprimir PDF**: Reduza o tamanho do arquivo PDF mantendo a melhor qualidade visual.
- **Proteger PDF**: Adicione criptografia militar AES-256 e senha para impedir acesso não autorizado.
- **Desbloquear PDF**: Remova senhas e restrições de permissão do arquivo.
- **Marca d'Água**: Adicione carimbos textuais ("CONFIDENCIAL", "RASCUNHO", etc.) com controle de opacidade e ângulo.

---

## 📂 Estrutura do Repositório

- **/Front-End**: Interface estática moderna em HTML5, CSS3 e Vanilla JS modular, com Dark Mode nativo e favicons vetoriais. [Veja o README do Front-End](./Front-End/README.md)
- **/Back-End**: API REST em Django 5+ com serviços modulares (`apps.pdf_tools.services`), suporte a `pikepdf`, `pdf2docx`, `PyMuPDF`, `Pillow`, `ReportLab` e `LibreOffice`. [Veja o README do Back-End](./Back-End/README.md)

---

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
# Interface disponível em http://localhost:3000/
```

> ⚠️ Use um servidor local para o Front-End (não abra o `.html` direto). O `type="module"` do JavaScript exige protocolo `http://`.
