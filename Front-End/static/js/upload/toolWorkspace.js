import { downloadBlob } from '../services/api.js';

export function setupToolWorkspace({
    accept = '.pdf,application/pdf',
    multiple = false,
    minFiles = 1,
    actionButtonText = 'Processar',
    getOptions = () => ({}),
    executeApi = async (files, options, onProgress) => {},
    onSuccessMessage = 'Arquivo processado com sucesso!',
}) {
    document.addEventListener('DOMContentLoaded', () => {
        const dropzone = document.getElementById('dropzone');
        const fileInput = document.getElementById('fileInput');
        const activeWorkspace = document.getElementById('activeWorkspace');
        const fileGrid = document.getElementById('fileGrid');
        const processBtn = document.getElementById('processBtn');
        const progressOverlay = document.getElementById('progressOverlay');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');

        if (!dropzone || !fileInput) return;

        fileInput.accept = accept;
        fileInput.multiple = multiple;

        let selectedFiles = [];

        // ─── Click no Dropzone ───────────────────────────────────────────────
        dropzone.addEventListener('click', (e) => {
            if (e.target.closest('button')) return;
            fileInput.click();
        });

        dropzone.querySelector('button')?.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });

        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
            fileInput.value = '';
        });

        // ─── Drag and Drop ───────────────────────────────────────────────────
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach((eventName) => {
            dropzone.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach((ev) => {
            dropzone.addEventListener(ev, () => dropzone.classList.add('dragover'), false);
        });

        ['dragleave', 'drop'].forEach((ev) => {
            dropzone.addEventListener(ev, () => dropzone.classList.remove('dragover'), false);
        });

        dropzone.addEventListener('drop', (e) => {
            handleFiles(e.dataTransfer.files);
        });

        // ─── Tratamento de arquivos ──────────────────────────────────────────
        function handleFiles(files) {
            const list = Array.from(files);
            if (list.length === 0) return;

            if (!multiple) {
                selectedFiles = [list[0]];
            } else {
                selectedFiles = [...selectedFiles, ...list];
            }
            updateWorkspace();
        }

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

        function renderFiles() {
            fileGrid.innerHTML = '';
            selectedFiles.forEach((file, index) => {
                const fileEl = document.createElement('div');
                fileEl.className = 'pdf-item';
                fileEl.draggable = multiple;
                fileEl.dataset.index = index;

                const isImage = file.type.startsWith('image/');
                const isWord = file.name.endsWith('.docx') || file.name.endsWith('.doc');

                let iconSvg = `
                    <svg class="pdf-preview-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="8" y2="13"></line>
                        <line x1="16" y1="17" x2="8" y2="17"></line>
                        <polyline points="10 9 9 9 8 9"></polyline>
                    </svg>
                `;

                if (isWord) {
                    iconSvg = `
                        <svg class="pdf-preview-icon" style="color: #2563eb;" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                            <path d="M10 12l2 4 2-4"></path>
                        </svg>
                    `;
                } else if (isImage) {
                    iconSvg = `
                        <svg class="pdf-preview-icon" style="color: #10b981;" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                            <circle cx="8.5" cy="8.5" r="1.5"></circle>
                            <polyline points="21 15 16 10 5 21"></polyline>
                        </svg>
                    `;
                }

                fileEl.innerHTML = `
                    <button class="remove-file" data-index="${index}" aria-label="Remover ${file.name}">×</button>
                    ${iconSvg}
                    <div class="pdf-name" title="${file.name}">${file.name}</div>
                    <div class="pdf-size">${formatFileSize(file.size)}</div>
                `;
                fileGrid.appendChild(fileEl);
            });

            if (multiple) {
                const addMoreBtn = document.createElement('div');
                addMoreBtn.className = 'pdf-item add-more-btn';
                addMoreBtn.setAttribute('role', 'button');
                addMoreBtn.innerHTML = `
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="12" y1="5" x2="12" y2="19"></line>
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    <div class="pdf-name">Adicionar mais</div>
                `;
                addMoreBtn.addEventListener('click', () => fileInput.click());
                fileGrid.appendChild(addMoreBtn);
                setupDragToReorder();
            }

            fileGrid.querySelectorAll('.remove-file').forEach((btn) => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const idx = parseInt(e.currentTarget.getAttribute('data-index'));
                    selectedFiles.splice(idx, 1);
                    updateWorkspace();
                });
            });
        }

        function setupDragToReorder() {
            let dragSrcIndex = null;
            fileGrid.querySelectorAll('.pdf-item[draggable="true"]').forEach((item) => {
                item.addEventListener('dragstart', (e) => {
                    dragSrcIndex = parseInt(item.dataset.index);
                    item.classList.add('dragging');
                    e.dataTransfer.effectAllowed = 'move';
                });

                item.addEventListener('dragend', () => {
                    item.classList.remove('dragging');
                    fileGrid.querySelectorAll('.pdf-item').forEach((i) => i.classList.remove('drag-over'));
                });

                item.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    e.dataTransfer.dropEffect = 'move';
                    fileGrid.querySelectorAll('.pdf-item').forEach((i) => i.classList.remove('drag-over'));
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

        // ─── Processamento do formulário ─────────────────────────────────────
        if (processBtn) {
            processBtn.addEventListener('click', async () => {
                if (selectedFiles.length < minFiles) {
                    showToast(`Selecione pelo menos ${minFiles} arquivo(s) para continuar.`, 'error');
                    return;
                }

                let options;
                try {
                    options = getOptions();
                } catch (err) {
                    showToast(err.message, 'error');
                    return;
                }

                progressOverlay.style.display = 'flex';
                progressBar.style.width = '0%';
                progressText.textContent = 'Enviando arquivo(s)...';
                processBtn.disabled = true;

                try {
                    const result = await executeApi(
                        multiple ? selectedFiles : selectedFiles[0],
                        options,
                        (progress) => {
                            progressBar.style.width = `${progress}%`;
                            if (progress < 60) {
                                progressText.textContent = `Enviando... ${progress}%`;
                            } else if (progress < 100) {
                                progressText.textContent = `Processando... ${progress}%`;
                            } else {
                                progressText.textContent = 'Concluído! Baixando...';
                            }
                        }
                    );

                    downloadBlob(result.blob, result.filename);

                    setTimeout(() => {
                        progressOverlay.style.display = 'none';
                        showToast(`✅ ${onSuccessMessage}`, 'success');
                        selectedFiles = [];
                        updateWorkspace();
                    }, 800);
                } catch (err) {
                    progressOverlay.style.display = 'none';
                    showToast(`❌ ${err.message}`, 'error');
                } finally {
                    processBtn.disabled = false;
                }
            });
        }

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

            requestAnimationFrame(() => toast.classList.add('toast-visible'));

            setTimeout(() => {
                toast.classList.remove('toast-visible');
                setTimeout(() => toast.remove(), 400);
            }, 4000);
        }
    });
}

