// O-RedMind App JavaScript

// Variables globales
window.socket = null;
window.isConnected = false;

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM chargé, initialisation Socket.IO');
    initializeSocket();
});

function initializeSocket() {
    console.log('Initialisation Socket.IO...');
    window.socket = io();
    
    window.socket.on('connect', function() {
        window.isConnected = true;
        updateConnectionStatus('Connecté', 'status-online');
        console.log('✅ Connecté au serveur O-RedMind');
    });
    
    window.socket.on('disconnect', function() {
        window.isConnected = false;
        updateConnectionStatus('Déconnecté', 'status-offline');
        console.log('❌ Déconnecté du serveur');
    });
    
    window.socket.on('error', function(data) {
        console.error('Erreur Socket.IO:', data.message);
        showNotification('Erreur: ' + data.message, 'danger');
    });
}

function updateConnectionStatus(text, className) {
    const statusElement = document.getElementById('connectionStatus');
    if (statusElement) {
        statusElement.textContent = text;
        statusElement.className = className;
    }
}

function showNotification(message, type = 'info') {
    // Création d'une notification Bootstrap toast
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                    data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '11';
    document.body.appendChild(container);
    return container;
}

// Utilitaires
function formatTimestamp(timestamp) {
    return new Date(timestamp * 1000).toLocaleTimeString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}