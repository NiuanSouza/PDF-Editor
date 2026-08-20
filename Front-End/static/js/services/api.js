/**
 * api.js — Módulo de comunicação com a API do backend
 *
 * A URL base da API é lida do atributo `data-api-url` do elemento <body>,
 * permitindo configuração fácil sem rebuild.
 *
 * Exemplo no HTML:
 *   <body data-api-url="https://pdf-editor-backend.onrender.com">
 *
 * Se não informado, usa o mesmo domínio (útil quando servidos juntos).
 */

const API_BASE_URL = (() => {
    const fromBody = document.body.getAttribute('data-api-url');
    if (fromBody) return fromBody.replace(/\/$/, ''); // Remove trailing slash
    return ''; // Mesmo domínio
})();

/**
 * Faz merge de múltiplos PDFs e retorna um Blob do resultado.
 * @param {File[]} files - Array de objetos File (tipo application/pdf)
 * @param {function(number): void} onProgress - Callback com progresso de 0 a 100
 * @returns {Promise<Blob>} - Blob do PDF resultante
 */
export function mergePdfs(files, onProgress = () => {}) {
    return new Promise((resolve, reject) => {
        const formData = new FormData();
        files.forEach(file => formData.append('files', file));

        const xhr = new XMLHttpRequest();

        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                // Upload: 0-70%
                const uploadPct = Math.round((e.loaded / e.total) * 70);
                onProgress(uploadPct);
            }
        });

        xhr.addEventListener('load', () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                // Processamento concluído: 100%
                onProgress(100);
                resolve(xhr.response);
            } else {
                let errorMsg = 'Erro ao juntar os PDFs.';
                try {
                    const errorData = JSON.parse(xhr.responseText);
                    errorMsg = errorData.error || errorMsg;
                } catch {}
                reject(new Error(errorMsg));
            }
        });

        xhr.addEventListener('error', () => {
            reject(new Error('Falha na conexão com o servidor. Verifique sua internet.'));
        });

        xhr.addEventListener('timeout', () => {
            reject(new Error('O servidor demorou muito para responder. Tente arquivos menores.'));
        });

        xhr.open('POST', `${API_BASE_URL}/api/merge/`);
        xhr.responseType = 'blob';
        xhr.timeout = 120000; // 2 minutos de timeout

        // Simular progresso de processamento após upload (70-95%)
        let processingProgress = 70;
        const processingInterval = setInterval(() => {
            if (processingProgress < 95) {
                processingProgress += 5;
                onProgress(processingProgress);
            } else {
                clearInterval(processingInterval);
            }
        }, 300);

        xhr.addEventListener('loadend', () => clearInterval(processingInterval));

        xhr.send(formData);
    });
}

/**
 * Dispara download de um Blob no navegador do usuário.
 * @param {Blob} blob - O arquivo a ser baixado
 * @param {string} filename - Nome sugerido para o arquivo
 */
export function downloadBlob(blob, filename = 'merged.pdf') {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}
