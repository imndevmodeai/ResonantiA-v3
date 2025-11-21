// Zepto Compression Interface - JavaScript

// State management
const state = {
    compressData: null,
    decompressData: null
};

// DOM Elements
const compressForm = document.getElementById('compress-form');
const decompressForm = document.getElementById('decompress-form');
const compressFileInput = document.getElementById('compress-file');
const compressTextInput = document.getElementById('compress-text');
const compressResults = document.getElementById('compress-results');
const decompressResults = document.getElementById('decompress-results');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    initializeFileInput();
});

// Event Listeners
function initializeEventListeners() {
    // Compression form
    if (compressForm) {
        compressForm.addEventListener('submit', handleCompress);
    }
    
    // Decompression form
    if (decompressForm) {
        decompressForm.addEventListener('submit', handleDecompress);
    }
    
    // Close results buttons
    const compressCloseBtn = document.getElementById('compress-close-results');
    const decompressCloseBtn = document.getElementById('decompress-close-results');
    
    if (compressCloseBtn) {
        compressCloseBtn.addEventListener('click', () => {
            compressResults.style.display = 'none';
        });
    }
    
    if (decompressCloseBtn) {
        decompressCloseBtn.addEventListener('click', () => {
            decompressResults.style.display = 'none';
        });
    }
    
    // Download buttons
    const downloadZepto = document.getElementById('download-zepto');
    const downloadCodex = document.getElementById('download-codex');
    const downloadStages = document.getElementById('download-stages');
    const downloadDecompressed = document.getElementById('download-decompressed');
    
    if (downloadZepto) {
        downloadZepto.addEventListener('click', () => {
            const zeptoSpr = state.compressData?.zepto_spr || '';
            const filename = state.compressData?.filename || 'zepto_spr';
            downloadFile('zepto', zeptoSpr, filename);
        });
    }
    
    if (downloadCodex) {
        downloadCodex.addEventListener('click', () => {
            const codex = state.compressData?.codex;
            const filename = state.compressData?.filename || 'codex';
            // Ensure codex is an object, not a string
            let codexObj = {};
            if (codex) {
                try {
                    codexObj = typeof codex === 'string' ? JSON.parse(codex) : codex;
                } catch (e) {
                    codexObj = {};
                }
            }
            // Always allow download, even if empty (user can see it's empty)
            downloadFile('codex', codexObj, filename);
        });
    }
    
    if (downloadStages) {
        downloadStages.addEventListener('click', () => {
            const stages = state.compressData?.compression_stages || [];
            const filename = state.compressData?.filename || 'stages';
            downloadFile('stages', stages, filename);
        });
    }
    
    if (downloadDecompressed) {
        downloadDecompressed.addEventListener('click', () => {
            const blob = new Blob([state.decompressData?.decompressed_text || ''], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'decompressed.txt';
            a.click();
            URL.revokeObjectURL(url);
        });
    }
    
    // Copy buttons
    document.querySelectorAll('.btn-copy').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const targetId = btn.getAttribute('data-target');
            const target = document.getElementById(targetId);
            if (target) {
                copyToClipboard(target.textContent);
                showToast('Copied to clipboard!', 'success');
            }
        });
    });
    
    // File input change
    if (compressFileInput) {
        compressFileInput.addEventListener('change', handleFileSelect);
    }
    
    // Text input change (clear file selection)
    if (compressTextInput) {
        compressTextInput.addEventListener('input', () => {
            if (compressFileInput) {
                compressFileInput.value = '';
                updateFileInfo('');
            }
        });
    }
}

// File Input Handling
function initializeFileInput() {
    if (compressFileInput) {
        // Drag and drop
        const fileLabel = compressFileInput.closest('.form-group')?.querySelector('.file-label');
        if (fileLabel) {
            fileLabel.addEventListener('dragover', (e) => {
                e.preventDefault();
                fileLabel.style.borderColor = 'var(--accent-primary)';
                fileLabel.style.background = 'var(--bg-hover)';
            });
            
            fileLabel.addEventListener('dragleave', () => {
                fileLabel.style.borderColor = '';
                fileLabel.style.background = '';
            });
            
            fileLabel.addEventListener('drop', (e) => {
                e.preventDefault();
                fileLabel.style.borderColor = '';
                fileLabel.style.background = '';
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    compressFileInput.files = files;
                    handleFileSelect();
                }
            });
        }
    }
}

function handleFileSelect() {
    const file = compressFileInput.files[0];
    if (file) {
        const fileSize = formatFileSize(file.size);
        updateFileInfo(`${file.name} (${fileSize})`);
        
        // Clear text input
        if (compressTextInput) {
            compressTextInput.value = '';
        }
    }
}

function updateFileInfo(text) {
    const fileInfo = document.getElementById('compress-file-info');
    if (fileInfo) {
        fileInfo.textContent = text;
    }
}

// Compression Handler
async function handleCompress(e) {
    e.preventDefault();
    
    const formData = new FormData();
    const targetStage = document.getElementById('target-stage')?.value || 'Zepto';
    
    // Get file or text
    const file = compressFileInput.files[0];
    if (file) {
        formData.append('file', file);
    } else if (compressTextInput && compressTextInput.value.trim()) {
        formData.append('text', compressTextInput.value);
    } else {
        showToast('Please select a file or enter text', 'error');
        return;
    }
    
    formData.append('target_stage', targetStage);
    
    // Show loading state
    const compressBtn = document.getElementById('compress-btn');
    setButtonLoading(compressBtn, true);
    
    try {
        const response = await fetch('/api/compress', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            state.compressData = data;
            displayCompressResults(data);
            showToast('Compression successful!', 'success');
        } else {
            showToast(data.error || 'Compression failed', 'error');
        }
    } catch (error) {
        console.error('Compression error:', error);
        showToast('Network error. Please try again.', 'error');
    } finally {
        setButtonLoading(compressBtn, false);
    }
}

// Decompression Handler
async function handleDecompress(e) {
    e.preventDefault();
    
    const zeptoText = document.getElementById('decompress-zepto')?.value.trim();
    if (!zeptoText) {
        showToast('Please enter Zepto SPR text', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('zepto_spr', zeptoText);
    
    const codexText = document.getElementById('decompress-codex')?.value.trim();
    if (codexText) {
        formData.append('codex', codexText);
    }
    
    const stagesText = document.getElementById('decompress-stages')?.value.trim();
    if (stagesText) {
        formData.append('compression_stages', stagesText);
    }
    
    // Show loading state
    const decompressBtn = document.getElementById('decompress-btn');
    setButtonLoading(decompressBtn, true);
    
    try {
        const response = await fetch('/api/decompress', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            state.decompressData = data;
            displayDecompressResults(data);
            showToast('Decompression successful!', 'success');
        } else {
            showToast(data.error || 'Decompression failed', 'error');
        }
    } catch (error) {
        console.error('Decompression error:', error);
        showToast('Network error. Please try again.', 'error');
    } finally {
        setButtonLoading(decompressBtn, false);
    }
}

// Display Results
function displayCompressResults(data) {
    // Update stats
    document.getElementById('compress-original-size').textContent = formatBytes(data.original_length);
    document.getElementById('compress-zepto-size').textContent = formatBytes(data.zepto_length);
    document.getElementById('compress-ratio').textContent = `${data.compression_ratio.toFixed(2)}:1`;
    document.getElementById('compress-time').textContent = `${(data.processing_time_sec || 0).toFixed(3)}s`;
    
    // Update Zepto output
    const zeptoOutput = document.getElementById('compress-zepto-output');
    if (zeptoOutput) {
        zeptoOutput.textContent = data.zepto_spr || '';
    }
    
    // Update Codex output - show full codex if available, otherwise show new entries
    const codexOutput = document.getElementById('compress-codex-output');
    if (codexOutput) {
        // Format codex as pretty JSON
        // Prefer full_codex if available, otherwise use new codex entries
        let codexToDisplay = '{}';
        let codexData = null;
        
        // Use full_codex if available, otherwise fall back to new codex entries
        if (data.full_codex && Object.keys(data.full_codex).length > 0) {
            codexData = data.full_codex;
        } else if (data.codex) {
            codexData = data.codex;
        }
        
        try {
            if (codexData) {
                const codexJson = typeof codexData === 'string' ? JSON.parse(codexData) : codexData;
                codexToDisplay = JSON.stringify(codexJson, null, 2);
            } else {
                codexToDisplay = '{}';
            }
        } catch (e) {
            // If codex is already a string or object, try to stringify it
            if (codexData) {
                codexToDisplay = typeof codexData === 'object' 
                    ? JSON.stringify(codexData, null, 2) 
                    : (codexData || '{}');
            }
        }
        codexOutput.textContent = codexToDisplay;
    }
    
    // Show results
    compressResults.style.display = 'block';
    compressResults.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function displayDecompressResults(data) {
    // Update stats
    document.getElementById('decompress-zepto-size').textContent = formatBytes(data.zepto_length);
    document.getElementById('decompress-output-size').textContent = formatBytes(data.decompressed_length);
    document.getElementById('decompress-time').textContent = `${(data.decompression_time_sec || 0).toFixed(3)}s`;
    
    // Update decompressed output
    const decompressOutput = document.getElementById('decompress-output');
    if (decompressOutput) {
        decompressOutput.textContent = data.decompressed_text;
    }
    
    // Show results
    decompressResults.style.display = 'block';
    decompressResults.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Download Functions
async function downloadFile(type, content, filename) {
    // Handle empty content (but allow empty codex to be downloaded)
    if (type === 'codex') {
        // Always allow codex download, even if empty - user can see it's empty
        if (!content || (typeof content === 'object' && Object.keys(content).length === 0)) {
            // Still download empty codex as {} so user can see it
            content = {};
        }
    } else if (!content) {
        showToast('No data to download', 'error');
        return;
    }
    
    try {
        // Clean filename
        const cleanFilename = filename.replace(/\.[^/.]+$/, '').replace(/[^a-zA-Z0-9_-]/g, '_');
        
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: type,
                content: content,
                filename: cleanFilename
            })
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            
            // Set proper filename with extension
            let downloadName = cleanFilename;
            if (type === 'zepto') {
                downloadName += '.txt';
            } else if (type === 'codex') {
                downloadName += '_codex.json';
            } else if (type === 'stages') {
                downloadName += '_stages.json';
            }
            
            a.download = downloadName;
            a.click();
            URL.revokeObjectURL(url);
            showToast('Download started', 'success');
        } else {
            const error = await response.json();
            showToast(error.error || 'Download failed', 'error');
        }
    } catch (error) {
        console.error('Download error:', error);
        showToast('Download error. Please try again.', 'error');
    }
}

// Utility Functions
function setButtonLoading(button, loading) {
    if (!button) return;
    
    const btnText = button.querySelector('.btn-text');
    const btnSpinner = button.querySelector('.btn-spinner');
    
    if (loading) {
        button.disabled = true;
        if (btnText) btnText.style.opacity = '0.7';
        if (btnSpinner) btnSpinner.style.display = 'block';
    } else {
        button.disabled = false;
        if (btnText) btnText.style.opacity = '1';
        if (btnSpinner) btnSpinner.style.display = 'none';
    }
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function formatFileSize(bytes) {
    return formatBytes(bytes);
}

function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
    }
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = getToastIcon(type);
    toast.innerHTML = `
        ${icon}
        <span class="toast-message">${message}</span>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.style.animation = 'toastSlideIn 0.3s ease reverse';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 5000);
}

function getToastIcon(type) {
    const icons = {
        success: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
        error: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>',
        warning: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>'
    };
    return icons[type] || icons.success;
}

