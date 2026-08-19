import { mergePdfs, downloadBlob } from '../services/api.js';

document.addEventListener('DOMContentLoaded', () => {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const activeWorkspace = document.getElementById('activeWorkspace');
    const fileGrid = document.getElementById('fileGrid');

    if (!dropzone) return;

    let selectedFiles = [];

    // ─── Dropzone — Clique para abrir o seletor de arquivos ───────────────────
    dropzone.addEventListener('click', (e) => {
        // Prevenir clique duplo se o clique veio do botão filho
        if (e.target.closest('button')) return;
        fileInput.click();
    });

    dropzone.querySelector('button')?.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
        // Limpar o input para permitir re-selecionar o mesmo arquivo
        fileInput.value = '';
    });

    // ─── Drag and Drop ────────────────────────────────────────────────────────
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
    });

    dropzone.addEventListener('drop', (e) => {
        handleFiles(e.dataTransfer.files);
    });

    // ─── Lidar com os arquivos selecionados ───────────────────────────────────
    function handleFiles(files) {
        const pdfFiles = Array.from(files).filter(
            file => file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
        );

        if (pdfFiles.length === 0) {
            showToast('Por favor, selecione apenas arquivos PDF.', 'error');
            return;
        }

        selectedFiles = [...selectedFiles, ...pdfFiles];
        updateWorkspace();
    }

    // ─── Atualizar a tela conforme os arquivos selecionados ───────────────────
    function updateWorkspace() {
        if (selectedFiles.length > 0) {
            dropzone.style.display = 'none';
            activeWorkspace.style.display = 'flex';
            renderFiles();
        } else {
            dropzone.style.display = 'flex';
            activeWorkspace.style.display = 'none';
        }
    }

    // ─── Renderizar os cards de arquivo no grid ───────────────────────────────
    function renderFiles() {
        fileGrid.innerHTML = '';
        selectedFiles.forEach((file, index) => {
            const fileEl = document.createElement('div');
            fileEl.className = 'pdf-item';
            fileEl.draggable = true;
            fileEl.dataset.index = index;
            fileEl.innerHTML = `
                <button class="remove-file" data-index="${index}" aria-label="Remover ${file.name}">×</button>
                <svg class="pdf-preview-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
                <div class="pdf-name" title="${file.name}">${file.name}</div>
                <div class="pdf-size">${formatFileSize(file.size)}</div>
            `;
            fileGrid.appendChild(fileEl);
        });

        // Botão de adicionar mais arquivos
        const addMoreBtn = document.createElement('div');
        addMoreBtn.className = 'pdf-item add-more-btn';
        addMoreBtn.setAttribute('role', 'button');
        addMoreBtn.setAttribute('aria-label', 'Adicionar mais PDFs');
        addMoreBtn.innerHTML = `
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            <div class="pdf-name">Adicionar mais</div>
        `;
        addMoreBtn.addEventListener('click', () => fileInput.click());
        fileGrid.appendChild(addMoreBtn);

        // Listeners de remoção
        fileGrid.querySelectorAll('.remove-file').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const index = parseInt(e.currentTarget.getAttribute('data-index'));
                selectedFiles.splice(index, 1);
                updateWorkspace();
            });
        });

        // Drag-to-reorder
        setupDragToReorder();
    }

    // ─── Drag-to-reorder dentro do grid ──────────────────────────────────────
    function setupDragToReorder() {
        let dragSrcIndex = null;

        fileGrid.querySelectorAll('.pdf-item[draggable]').forEach(item => {
            item.addEventListener('dragstart', (e) => {
                dragSrcIndex = parseInt(item.dataset.index);
                item.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
            });

            item.addEventListener('dragend', () => {
                item.classList.remove('dragging');
                fileGrid.querySelectorAll('.pdf-item').forEach(i => i.classList.remove('drag-over'));
            });

            item.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                fileGrid.querySelectorAll('.pdf-item').forEach(i => i.classList.remove('drag-over'));
                item.classList.add('drag-over');
            });

            item.addEventListener('drop', (e) => {
                e.preventDefault();
                const targetIndex = parseInt(item.dataset.index);
                if (dragSrcIndex !== null && dragSrcIndex !== targetIndex) {
                    const moved = selectedFiles.splice(dragSrcIndex, 1)[0];
                    selectedFiles.splice(targetIndex, 0, moved);
                    renderFiles();
                }
                dragSrcIndex = null;
            });
        });
    }

    // ─── Botão "Juntar PDF" — chama a API real ────────────────────────────────
    const processBtn = document.getElementById('processBtn');
    const progressOverlay = document.getElementById('progressOverlay');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');

    if (processBtn) {
        processBtn.addEventListener('click', async () => {
            if (selectedFiles.length < 2) {
                showToast('Adicione pelo menos 2 arquivos PDF para juntar.', 'error');
                return;
            }

            // Mostrar overlay de progresso
            progressOverlay.style.display = 'flex';
            progressBar.style.width = '0%';
            progressText.textContent = 'Enviando arquivos...';
            processBtn.disabled = true;

            try {
                const blob = await mergePdfs(selectedFiles, (progress) => {
                    progressBar.style.width = `${progress}%`;
                    if (progress < 70) {
                        progressText.textContent = `Enviando... ${progress}%`;
                    } else if (progress < 100) {
                        progressText.textContent = `Processando... ${progress}%`;
                    } else {
                        progressText.textContent = 'Concluído! Baixando...';
                    }
                });

                // Disparar download
                const fileName = `merged_${selectedFiles.length}_arquivos.pdf`;
                downloadBlob(blob, fileName);

                // Feedback de sucesso
                setTimeout(() => {
                    progressOverlay.style.display = 'none';
                    showToast(`✅ ${selectedFiles.length} PDFs unidos com sucesso!`, 'success');
                    // Resetar workspace
                    selectedFiles = [];
                    updateWorkspace();
                }, 800);

            } catch (error) {
                progressOverlay.style.display = 'none';
                showToast(`❌ ${error.message}`, 'error');
            } finally {
                processBtn.disabled = false;
            }
        });
    }

    // ─── Utilitários ──────────────────────────────────────────────────────────
    function formatFileSize(bytes) {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / 1048576).toFixed(1)} MB`;
    }

    function showToast(message, type = 'info') {
        const existing = document.querySelector('.toast-notification');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);

        // Animar entrada
        requestAnimationFrame(() => toast.classList.add('toast-visible'));

        setTimeout(() => {
            toast.classList.remove('toast-visible');
            setTimeout(() => toast.remove(), 400);
        }, 4000);
    }
});
