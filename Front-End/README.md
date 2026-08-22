# Front-End

> Interface de usuário para manipulação de PDFs — Drag & Drop, reordenação, Dark Mode e progresso real de upload, tudo em Vanilla HTML/CSS/JS.

## 🎨 Layout e Telas

O Front-End é composto por duas telas principais:

**1. Home (`index.html`)** — Landing page com a grade de ferramentas disponíveis.

**2. Juntar PDF (`merge.html`)** — Tela principal de uso:
- **Área de Drag & Drop**: Zona pontilhada onde o usuário arrasta os PDFs ou clica para selecionar
- **Grid de arquivos**: Cada PDF aparece como um card com nome, tamanho e botão de remoção. Os cards são arrastáveis para reordenação
- **Sidebar de ações**: Botão "Juntar PDF" que dispara o upload real para o Back-End com barra de progresso
- **Toast notifications**: Feedback visual de sucesso ou erro após o processamento

**Fluxo de uso**:
```
Arrastar PDFs → Reordenar → Clicar "Juntar PDF" → Barra de progresso → Download automático
```

## 🛠 Tecnologias e Bibliotecas

- **HTML5** — estrutura semântica com elementos nativos
- **CSS3 / ITCSS** — organização modular (base, layout, components, animations). Dark Mode via variáveis CSS e `data-theme`
- **Vanilla JS (ES Modules)** — sem frameworks ou bundlers. Usa `import/export` nativo do navegador
- **XMLHttpRequest** — chamada à API com progresso real de upload via `xhr.upload.onprogress`

## 🚀 Como Rodar o Front-End

### Execução local

```bash
cd Front-End
python3 -m http.server 3000
# Acesse: http://localhost:3000/merge.html
```

> ⚠️ Não abra o `.html` diretamente como arquivo (`file://`). O `type="module"` do JavaScript exige protocolo `http://` — use o Live Server do VS Code ou o comando acima.

### Via Docker

```bash
cd Front-End
docker build -t pdf-editor-frontend .
docker run -p 3000:80 pdf-editor-frontend
# Acesse: http://localhost:3000
```
