// O-RedMind Chat JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeChat();
    loadChatHistory();
});

function initializeChat() {
    console.log('Initialisation du chat...');
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        console.log('MessageInput trouvé, ajout event listener');
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    } else {
        console.error('MessageInput non trouvé!');
    }
    
    // Événements Socket.IO pour le chat
    if (window.socket) {
        window.socket.on('message_received', function(data) {
            displayMessage(data.message);
        });
        
        window.socket.on('ai_thinking', function(data) {
            displayThinkingMessage(data.message);
        });
        
        window.socket.on('ai_response', function(data) {
            removeThinkingMessage();
            displayMessage(data.message);
        });
        
        window.socket.on('chat_history', function(data) {
            displayChatHistory(data.messages);
        });
        
        window.socket.on('history_cleared', function() {
            clearChatDisplay();
            showNotification('Historique effacé', 'success');
        });
    }
}

function sendMessage() {
    console.log('sendMessage() appelée');
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    console.log('Message:', message);
    
    if (!message) {
        console.log('Message vide, abandon');
        return;
    }
    
    if (!window.isConnected || !window.socket) {
        console.error('Socket non connecté:', {isConnected: window.isConnected, socket: window.socket});
        showNotification('Non connecté au serveur', 'danger');
        return;
    }
    
    console.log('Émission du message vers le serveur');
    window.socket.emit('send_message', {
        message: message,
        modality: 'text',
        attachments: []
    });
    
    messageInput.value = '';
    console.log('Message envoyé et input vidé');
}

function displayMessage(message) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${message.message_type}`;
    
    let content = `
        <div class="message-content">${escapeHtml(message.content)}</div>
        <div class="message-meta">
            <small class="text-muted">${formatTimestamp(message.timestamp)}</small>
    `;
    
    if (message.reasoning_type) {
        content += `<span class="badge bg-secondary reasoning-type">${message.reasoning_type}</span>`;
    }
    
    if (message.confidence) {
        const confidencePercent = Math.round(message.confidence * 100);
        content += `<span class="badge bg-info confidence-badge">${confidencePercent}%</span>`;
    }
    
    content += '</div>';
    messageDiv.innerHTML = content;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function displayThinkingMessage(message) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const thinkingDiv = document.createElement('div');
    thinkingDiv.className = 'chat-message system thinking';
    thinkingDiv.id = 'thinkingMessage';
    thinkingDiv.innerHTML = `
        <div class="message-content">
            <i class="fas fa-spinner fa-spin"></i> ${escapeHtml(message)}
        </div>
    `;
    
    chatMessages.appendChild(thinkingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeThinkingMessage() {
    const thinkingMessage = document.getElementById('thinkingMessage');
    if (thinkingMessage) {
        thinkingMessage.remove();
    }
}

function displayChatHistory(messages) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    chatMessages.innerHTML = '';
    
    messages.forEach(message => {
        displayMessage(message);
    });
}

function loadChatHistory() {
    if (socket && isConnected) {
        socket.emit('get_history');
    }
}

function clearChat() {
    if (confirm('Êtes-vous sûr de vouloir effacer tout l'historique ?')) {
        if (socket && isConnected) {
            socket.emit('clear_history');
        }
    }
}

function clearChatDisplay() {
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        chatMessages.innerHTML = '';
    }
}

function showUpload() {
    console.log('showUpload() appelée');
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        console.log('FileInput trouvé, ouverture');
        fileInput.click();
    } else {
        console.error('FileInput non trouvé!');
    }
}

function handleFileSelect(input) {
    const file = input.files[0];
    if (!file) return;
    
    showNotification('Upload de fichier en cours...', 'info');
    
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Fichier uploadé avec succès', 'success');
            // TODO: Traiter le fichier uploadé
        } else {
            showNotification('Erreur upload: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        showNotification('Erreur upload: ' + error.message, 'danger');
    });
    
    input.value = '';
}