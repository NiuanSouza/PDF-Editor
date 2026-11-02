/**
 * api.js — Módulo central de comunicação com a API do backend
 */

const API_BASE_URL = (() => {
    const fromBody = document.body.getAttribute('data-api-url');
    if (fromBody) return fromBody.replace(/\/$/, '');
    return '';
})();

/**
 * Executa uma requisição POST multipart/form-data retornando Blob e nome do arquivo sugerido pelo servidor.
 */
function sendRequest(endpoint, formData, onProgress = () => {}) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const uploadPct = Math.round((e.loaded / e.total) * 60);
                onProgress(uploadPct);
            }
        });

        xhr.addEventListener('load', () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                onProgress(100);

                let filename = null;
                const disposition = xhr.getResponseHeader('Content-Disposition');
                if (disposition && disposition.indexOf('filename=') !== -1) {
                    const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
                    if (matches && matches[1]) {
                        filename = matches[1].replace(/['"]/g, '');
                    }
                }

                resolve({ blob: xhr.response, filename });
            } else {
                let errorMsg = 'Erro ao processar a solicitação.';
                try {
                    const reader = new FileReader();
                    reader.onload = () => {
                        try {
                            const errJson = JSON.parse(reader.result);
                            reject(new Error(errJson.error || errorMsg));
                        } catch {
                            reject(new Error(errorMsg));
                        }
                    };
                    reader.readAsText(xhr.response);
                    return;
                } catch {
                    reject(new Error(errorMsg));
                }
            }
        });

        xhr.addEventListener('error', () => {
            reject(new Error('Falha na conexão com o servidor. Verifique sua conexão de rede.'));
        });

        xhr.addEventListener('timeout', () => {
            reject(new Error('O tempo limite de processamento foi atingido. Tente com arquivos menores.'));
        });

        xhr.open('POST', `${API_BASE_URL}${endpoint}`);
        xhr.responseType = 'blob';
        xhr.timeout = 180000; // 3 minutos

        // Simula progresso suave de processamento enquanto o servidor calcula
        let processingProgress = 60;
        const processingInterval = setInterval(() => {
            if (processingProgress < 95) {
                processingProgress += 5;
                onProgress(processingProgress);
            } else {
                clearInterval(processingInterval);
            }
        }, 400);

        xhr.addEventListener('loadend', () => clearInterval(processingInterval));
        xhr.send(formData);
    });
}

/** 1. Juntar PDF */
export async function mergePdfs(files, onProgress) {
    const formData = new FormData();
    files.forEach(f => formData.append('files', f));
    const result = await sendRequest('/api/merge/', formData, onProgress);
    return { blob: result.blob, filename: result.filename || 'merged.pdf' };
}

/** 2. Dividir PDF */
export async function splitPdf(file, options = {}, onProgress) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('mode', options.mode || 'all');
    if (options.pageRange) {
        formData.append('page_range', options.pageRange);
    }
    const result = await sendRequest('/api/split/', formData, onProgress);
    return { blob: result.blob, filename: result.filename || (options.mode === 'all' ? 'paginas.zip' : 'dividido.pdf') };
}

/** 3. Comprimir PDF */
export async function compressPdf(file, options = {}, onProgress) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('level', options.level || 'recommended');
    const result = await sendRequest('/api/compress/', formData, onProgress);
    return { blob: result.blob, filename: result.filename || 'comprimido.pdf' };
}

/** 4. Word para PDF */
export async function wordToPdf(file, onProgress) {
    const formData = new FormData();
    formData.append('file', file);
    const result = await sendRequest('/api/word-to-pdf/', formData, onProgress);
    const defaultName = file.name ? `${file.name.replace(/\.[^/.]+$/, '')}.pdf` : 'convertido.pdf';
    return { blob: result.blob, filename: result.filename || defaultName };
}

/** 5. PDF para Word */
export async function pdfToWord(file, onProgress) {
    const formData = new FormData();
    formData.append('file', file);
    const result = await sendRequest('/api/pdf-to-word/', formData, onProgress);
    const defaultName = file.name ? `${file.name.replace(/\.[^/.]+$/, '')}.docx` : 'documento.docx';
    return { blob: result.blob, filename: result.filename || defaultName };
}

/** 6. PDF para Imagens */
export async function pdfToImages(file, options = {}, onProgress) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('format', options.format || 'jpg');
    formData.append('dpi', options.dpi || 150);
    const result = await sendRequest('/api/pdf-to-images/', formData, onProgress);
    return { blob: result.blob, filename: result.filename || 'imagens.zip' };
}

/** 7. Imagens para PDF */
export async function imagesToPdf(files, onProgress) {
    const formData = new FormData();
    files.forEach(f => formData.append('files', f));
    const result = await sendRequest('/api/images-to-pdf/', formData, onProgress);
    return { blob: result.blob, filename: result.filename || 'imagens.pdf' };
}

/** 8. Proteger PDF */
export async function protectPdf(file, password, onProgress) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('password', password);
    const result = await sendRequest('/api/protect/', formData, onProgress);
    return { blob: result.blob, filename: result.filename || 'protegido.pdf' };
}

/** 9. Desbloquear PDF */
export async function unlockPdf(file, password, onProgress) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('password', password);
    const result = await sendRequest('/api/unlock/', formData, onProgress);
    return { blob: result.blob, filename: result.filename || 'desbloqueado.pdf' };
}

/** 10. Rotacionar PDF */
export async function rotatePdf(file, options = {}, onProgress) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('angle', options.angle || 90);
    formData.append('page_selection', options.pageSelection || 'all');
    const result = await sendRequest('/api/rotate/', formData, onProgress);
    return { blob: result.blob, filename: result.filename || 'rotacionado.pdf' };
}

/** 11. Marca d'Água */
export async function watermarkPdf(file, options = {}, onProgress) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('text', options.text || '');
    formData.append('opacity', options.opacity || 0.3);
    formData.append('rotation', options.rotation || 45);
    formData.append('font_size', options.fontSize || 42);
    const result = await sendRequest('/api/watermark/', formData, onProgress);
    return { blob: result.blob, filename: result.filename || 'marca_dagua.pdf' };
}

/**
 * Dispara o download de um Blob no navegador.
 */
export function downloadBlob(blob, filename = 'download.pdf') {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}
