# Front-End

> Interface de usuário moderna para manipulação e conversão de PDFs — Drag & Drop, reordenação de páginas, Dark Mode nativo e progresso real de upload, tudo em Vanilla HTML5/CSS3/JS.

## 🎨 Layout e Telas

O Front-End é composto por páginas dedicadas para cada utilitário com identidade visual unificada e favicon profissional:

1. **Home (`index.html`)** — Grade completa com as 11 ferramentas organizadas por categorias (*Organizar*, *Converter*, *Otimizar*, *Segurança*).
2. **Juntar PDF (`merge.html`)**
3. **Dividir PDF (`split.html`)**
4. **Comprimir PDF (`compress.html`)**
5. **Word para PDF (`word-to-pdf.html`)**
6. **PDF para Word (`pdf-to-word.html`)**
7. **PDF para Imagens (`pdf-to-img.html`)**
8. **Imagens para PDF (`img-to-pdf.html`)**
9. **Proteger PDF (`protect.html`)**
10. **Desbloquear PDF (`unlock.html`)**
11. **Rotacionar PDF (`rotate.html`)**
12. **Marca d'Água (`watermark.html`)**

## 🛠 Tecnologias e Bibliotecas

- **HTML5** — estrutura semântica com elementos nativos
- **CSS3 / ITCSS** — organização modular (base, layout, components, animations, tool). Dark Mode via variáveis CSS e `data-theme`
- **Vanilla JS (ES Modules)** — sem dependência de frameworks. Utiliza controladores modulares (`toolWorkspace.js` e `api.js`)
- **Favicon Vetorial** — formato `.svg` de alta resolução com fallback `.ico` e touch icon

## 🚀 Como Rodar o Front-End

```bash
cd Front-End
python3 -m http.server 3000
# Acesse: http://localhost:3000/
```
