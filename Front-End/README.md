# Front-End

> Interface de usuário para manipulação de PDFs — Drag & Drop, reordenação, Dark Mode e progresso real de upload, tudo em Vanilla HTML/CSS/JS.

## 🎨 Layout e Telas

O Front-End é composto por duas telas principais:

**1. Home (`index.html`)** — Landing page com a grade de ferramentas disponíveis. Ao clicar em uma ferramenta, o usuário é direcionado para a tela correspondente.

**2. Juntar PDF (`merge.html`)** — Tela principal de uso:
- **Área de Drag & Drop**: Zona pontilhada onde o usuário arrasta os PDFs ou clica para selecionar pelo explorer
- **Grid de arquivos**: Após selecionar, cada PDF aparece como um card com nome, tamanho e botão de remoção. Os cards são arrastáveis para reordenação
- **Sidebar de ações**: Botão "Juntar PDF" que dispara o upload real para o Back-End e exibe barra de progresso
- **Toast notifications**: Feedback visual de sucesso ou erro após o processamento

**Fluxo de uso**:
```
Arrastar PDFs → Reordenar → Clicar "Juntar PDF" → Barra de progresso → Download automático
```

A URL do Back-End é configurável via atributo `data-api-url` na tag `<body>` do `merge.html`, sem necessidade de rebuild.

## 🛠 Tecnologias e Bibliotecas

- **HTML5** — estrutura semântica com elementos nativos (`<dialog>`, `<input type="file" multiple>`)
- **CSS3 / ITCSS** — organização modular (base, layout, components, animations). Dark Mode via variáveis CSS e `data-theme`
- **Vanilla JS (ES Modules)** — sem frameworks ou bundlers. Usa `import/export` nativo do navegador
- **Fetch API / XMLHttpRequest** — chamada à API real com progresso de upload via `xhr.upload.onprogress`

## 🚀 Como Rodar o Front-End

### Opção 1 — Servidor local (recomendado para desenvolvimento)

```bash
cd Front-End
python3 -m http.server 3000
# Acesse: http://localhost:3000/merge.html
```

> ⚠️ Não abra o `.html` diretamente como arquivo (`file://`). O `type="module"` do JavaScript exige protocolo `http://` — use o Live Server do VS Code ou o comando acima.

### Opção 2 — Docker / Nginx

```bash
cd Front-End
docker build -t pdf-editor-frontend .
docker run -p 3000:80 pdf-editor-frontend
# Acesse: http://localhost:3000
```

### Configuração para produção

Antes de fazer o deploy, edite `merge.html` e aponte `data-api-url` para a URL do seu Back-End no Render:

```html
<body data-api-url="https://pdf-editor-backend.onrender.com">
```

### Deploy no Render.com (Static Site)

1. Conecte o repositório (pasta `Front-End` como Root Directory)
2. **Publish Directory**: `.`
3. Deploy! O site ficará disponível em `https://pdf-editor-frontend.onrender.com`
