#!/usr/bin/env python3
"""
O-RedMind Interface Web
======================

Interface web moderne et responsive pour O-RedMind,
le système d'IA personnel respectueux de la vie privée.

Auteur: Système OpenRed 2025
Licence: MIT - Souveraineté Numérique Totale
"""

import os
import json
import time
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import uuid
import base64
import secrets
from io import BytesIO

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.utils import secure_filename
from PIL import Image
import markdown

# Import des modules O-RedMind
try:
    from oredmind_core import ORedMindCore, ConversationStyle, CreativeTask
    from moteur_intelligence_locale import (
        LocalLanguageModel, MultimodalProcessor, ReasoningEngine,
        ModalityType, ReasoningType, MultimodalInput
    )
    from ollama_integration import OllamaIntegration
    from personal_memory import PersonalMemoryManager, find_existing_user_profile
except ImportError:
    # Fallback pour les imports directs
    import oredmind_core
    import moteur_intelligence_locale
    import ollama_integration
    import personal_memory
    from oredmind_core import ORedMindCore, ConversationStyle, CreativeTask
    from moteur_intelligence_locale import (
        LocalLanguageModel, MultimodalProcessor, ReasoningEngine,
        ModalityType, ReasoningType, MultimodalInput
    )
    from ollama_integration import OllamaIntegration
    from personal_memory import PersonalMemoryManager, find_existing_user_profile

# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration Flask
app = Flask(__name__, 
           template_folder=str(Path(__file__).parent.parent.parent / "web" / "templates"),
           static_folder=str(Path(__file__).parent.parent.parent / "web" / "static"))
app.config['SECRET_KEY'] = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configuration SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configuration des uploads
UPLOAD_FOLDER = Path.home() / ".openred" / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True, parents=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'wav', 'mp3', 'mp4', 'py', 'js', 'html', 'css'}

@dataclass
class ChatMessage:
    """Message de chat"""
    id: str
    user_id: str
    content: str
    message_type: str  # 'user', 'ai', 'system'
    modality: str
    timestamp: float
    attachments: List[Dict[str, Any]]
    reasoning_type: Optional[str] = None
    confidence: Optional[float] = None

class ORedMindWebInterface:
    """Interface web pour O-RedMind avec intégration Ollama"""
    
    def __init__(self):
        self.oredmind_core = None
        self.ollama = None
        self.active_sessions = {}
        self.chat_history = {}
        self.personal_memories = {}  # Gestionnaires de mémoire par utilisateur
        self.initialize_core()
        self.initialize_ollama()
    
    def initialize_core(self):
        """Initialise le cœur O-RedMind avec génération automatique d'identité"""
        try:
            fort_path = Path.home() / ".openred"
            fort_path.mkdir(exist_ok=True, parents=True)
            
            # Configuration de l'utilisateur
            config_file = fort_path / "user_config.json"
            
            if config_file.exists():
                # Chargement de la configuration existante
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                user_id = config['user_id']
                user_key = base64.b64decode(config['user_key'])
            else:
                # Génération d'une nouvelle identité
                user_id = f"oredmind_user_{uuid.uuid4().hex[:12]}"
                user_key = secrets.token_bytes(32)  # Clé de chiffrement 256-bit
                
                # Sauvegarde de la configuration
                config = {
                    'user_id': user_id,
                    'user_key': base64.b64encode(user_key).decode('utf-8'),
                    'created_at': datetime.now().isoformat(),
                    'version': '1.0'
                }
                
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2)
                
                logger.info(f"🆔 Nouvelle identité O-RedMind générée: {user_id}")
            
            # Initialisation du cœur avec l'identité
            self.oredmind_core = ORedMindCore(fort_path, user_id, user_key)
            logger.info("✅ O-RedMind Core initialisé avec mémoire personnelle")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation O-RedMind: {e}")
            self.oredmind_core = None
    
    def initialize_ollama(self):
        """Initialise l'intégration Ollama"""
        try:
            self.ollama = OllamaIntegration()
            if self.ollama.is_connected:
                # Auto-sélection du meilleur modèle disponible
                recommended = self.ollama.get_recommended_model(['chat'])
                if recommended:
                    self.ollama.set_model(recommended)
                    logger.info(f"✅ Ollama initialisé avec {recommended}")
                else:
                    logger.info("✅ Ollama connecté mais aucun modèle disponible")
            else:
                logger.info("ℹ️  Ollama non disponible, mode fallback activé")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Ollama: {e}")
            self.ollama = None
    
    def get_user_session(self, session_id: str) -> Dict[str, Any]:
        """Récupère ou crée une session utilisateur"""
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                'user_id': f"user_{uuid.uuid4().hex[:8]}",
                'profile': 'Professionnel',  # Profil par défaut
                'preferences': {
                    'reasoning_type': 'analytical',
                    'response_length': 'medium',
                    'creativity_level': 0.7
                },
                'created_at': time.time()
            }
            self.chat_history[session_id] = []
        
        return self.active_sessions[session_id]
    
    def get_personal_memory(self, user_id: str) -> PersonalMemoryManager:
        """Récupère ou crée un gestionnaire de mémoire personnelle"""
        if user_id not in self.personal_memories:
            memory_path = Path.home() / ".openred" / "memory"
            self.personal_memories[user_id] = PersonalMemoryManager(user_id, memory_path)
            logger.info(f"🧠 Gestionnaire mémoire créé pour {user_id}")
        
        return self.personal_memories[user_id]
    
    def _build_enhanced_prompt(self, message: str, personal_context: str, additional_context: str = "") -> str:
        """Construit un prompt enrichi avec le contexte personnel"""
        enhanced_prompt = message
        
        if personal_context and personal_context != "Aucune information personnelle mémorisée.":
            enhanced_prompt = f"Contexte personnel de l'utilisateur:\n{personal_context}\n\nMessage: {message}"
        
        if additional_context:
            enhanced_prompt = f"Contexte supplémentaire:\n{additional_context}\n\n{enhanced_prompt}"
        
        return enhanced_prompt
    
    def _generate_with_ollama(self, enhanced_prompt: str, bicouche_response: str) -> str:
        """Génère une réponse avec Ollama en utilisant le contexte O-RedMind"""
        if not self.ollama_active:
            return bicouche_response
        
        try:
            final_prompt = f"""
Contexte O-RedMind: {bicouche_response}

Message utilisateur enrichi: {enhanced_prompt}

Génère une réponse professionnelle et personnalisée en tenant compte du contexte O-RedMind et des informations personnelles."""
            
            response = self.ollama_client.chat(
                model=self.current_model,
                messages=[{
                    'role': 'user',
                    'content': final_prompt
                }]
            )
            
            return response['message']['content']
        except Exception as e:
            logger.error(f"❌ Erreur génération Ollama: {e}")
            return bicouche_response
    
    def add_chat_message(self, session_id: str, message: ChatMessage):
        """Ajoute un message à l'historique"""
        if session_id not in self.chat_history:
            self.chat_history[session_id] = []
        
        self.chat_history[session_id].append(message)
        
        # Limite l'historique à 100 messages
        if len(self.chat_history[session_id]) > 100:
            self.chat_history[session_id] = self.chat_history[session_id][-100:]

# Instance globale
oredmind_interface = ORedMindWebInterface()

def allowed_file(filename: str) -> bool:
    """Vérifie si le fichier est autorisé"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Page d'accueil"""
    session_id = session.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
    
    user_session = oredmind_interface.get_user_session(session_id)
    return render_template('index.html', 
                         user_session=user_session,
                         chat_history=oredmind_interface.chat_history.get(session_id, []))

@app.route('/chat')
def chat():
    """Interface de chat"""
    session_id = session.get('session_id')
    if not session_id:
        return redirect(url_for('index'))
    
    user_session = oredmind_interface.get_user_session(session_id)
    return render_template('chat.html',
                         user_session=user_session,
                         reasoning_types=[rt.value for rt in ReasoningType],
                         modality_types=[mt.value for mt in ModalityType])

@app.route('/settings')
def settings():
    """Paramètres utilisateur"""
    session_id = session.get('session_id')
    if not session_id:
        return redirect(url_for('index'))
    
    user_session = oredmind_interface.get_user_session(session_id)
    return render_template('settings.html', user_session=user_session)

@app.route('/debug')
def debug():
    """Page de debug pour tester les boutons"""
    session_id = session.get('session_id')
    if not session_id:
        session['session_id'] = str(uuid.uuid4())
        session_id = session['session_id']
    
    return render_template('chat_debug.html')

@app.route('/simple')
def simple_chat():
    """Chat simple pour diagnostic"""
    # Force la création d'une session
    session_id = session.get('session_id')
    if not session_id:
        session['session_id'] = str(uuid.uuid4())
        session_id = session['session_id']
        logger.info(f"🆔 Nouvelle session créée: {session_id}")
    else:
        logger.info(f"🆔 Session existante: {session_id}")
    
    # Pré-initialisation de la session utilisateur
    user_session = oredmind_interface.get_user_session(session_id)
    logger.info(f"👤 Session utilisateur préparée: {user_session['user_id']}")
    
    # HTML direct pour éviter les problèmes de template
    html_content = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>O-RedMind Chat Simple</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
    <style>
        body { background-color: #f8f9fa; }
        .chat-container { max-width: 800px; margin: 20px auto; }
        .chat-messages { height: 400px; overflow-y: auto; background: white; border: 1px solid #ddd; padding: 15px; }
        .message { margin-bottom: 10px; padding: 8px 12px; border-radius: 8px; }
        .message.user { background-color: #007bff; color: white; margin-left: 50px; }
        .message.ai { background-color: #e9ecef; margin-right: 50px; }
        .typing { font-style: italic; color: #6c757d; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h4><i class="fas fa-robot"></i> O-RedMind Chat Simple - Test Boutons</h4>
                <small id="connectionStatus">Connexion...</small>
            </div>
            
            <div class="chat-messages" id="chatMessages">
                <div class="message ai">🤖 Bonjour ! Interface de test chargée. Testez les boutons ci-dessous.</div>
            </div>
            
            <div class="card-footer">
                <div class="input-group">
                    <input type="text" class="form-control" id="messageInput" 
                           placeholder="Tapez votre message et appuyez sur Entrée..." value="Test message">
                    <button class="btn btn-outline-secondary" id="uploadBtn">
                        <i class="fas fa-paperclip"></i>
                    </button>
                    <button class="btn btn-primary" id="sendBtn">
                        <i class="fas fa-paper-plane"></i> Envoyer
                    </button>
                </div>
                <input type="file" id="fileInput" style="display: none;">
                
                <div class="mt-2">
                    <button class="btn btn-info btn-sm" onclick="testAlert()">Test Alert</button>
                    <button class="btn btn-warning btn-sm" onclick="testConsole()">Test Console</button>
                    <button class="btn btn-success btn-sm" onclick="testElements()">Test Elements</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        console.log('🚀 Script chargé directement');
        
        // Variables globales
        let socket = null;
        let isConnected = false;
        
        // Tests de base
        function testAlert() {
            alert('✅ JavaScript fonctionne !');
            addMessage('Test Alert exécuté', 'ai');
        }
        
        function testConsole() {
            console.log('📝 Test Console exécuté');
            addMessage('Regardez la console (F12)', 'ai');
        }
        
        function testElements() {
            const messageInput = document.getElementById('messageInput');
            const sendBtn = document.getElementById('sendBtn');
            const uploadBtn = document.getElementById('uploadBtn');
            const fileInput = document.getElementById('fileInput');
            
            console.log('🔍 Test des éléments:', {
                messageInput: !!messageInput,
                sendBtn: !!sendBtn,
                uploadBtn: !!uploadBtn,
                fileInput: !!fileInput
            });
            
            addMessage('Elements trouvés: ' + 
                      (messageInput ? '✅' : '❌') + ' Input, ' +
                      (sendBtn ? '✅' : '❌') + ' Send, ' +
                      (uploadBtn ? '✅' : '❌') + ' Upload', 'ai');
        }
        
        // Elements DOM
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const uploadBtn = document.getElementById('uploadBtn');
        const fileInput = document.getElementById('fileInput');
        const chatMessages = document.getElementById('chatMessages');
        const connectionStatus = document.getElementById('connectionStatus');
        
        // Fonction d'envoi de message
        function sendMessage() {
            console.log('📤 sendMessage() appelée');
            
            if (!messageInput) {
                alert('❌ messageInput non trouvé');
                return;
            }
            
            const message = messageInput.value.trim();
            console.log('Message à envoyer:', message);
            
            if (!message) {
                alert('Message vide');
                return;
            }
            
            // Affichage immédiat du message utilisateur
            addMessage(message, 'user');
            messageInput.value = '';
            
            // Envoi via Socket.IO si connecté
            if (socket && isConnected) {
                console.log('Envoi via Socket.IO');
                socket.emit('send_message', {
                    message: message,
                    modality: 'text',
                    attachments: []
                });
            } else {
                console.warn('Socket non connecté, simulation réponse');
                setTimeout(() => {
                    addMessage('Réponse simulée: "' + message + '"', 'ai');
                }, 1000);
            }
        }
        
        // Fonction d'upload
        function showUpload() {
            console.log('📎 showUpload() appelée');
            if (fileInput) {
                addMessage('Ouverture sélecteur de fichier...', 'ai');
                fileInput.click();
            } else {
                alert('❌ fileInput non trouvé');
            }
        }
        
        // Ajout d'un message à l'interface
        function addMessage(content, type) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.textContent = (type === 'user' ? '👤 ' : '🤖 ') + content;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        // Initialisation Socket.IO
        function initSocket() {
            console.log('🔌 Initialisation Socket.IO');
            socket = io();
            
            socket.on('connect', function() {
                isConnected = true;
                connectionStatus.textContent = '✅ Connecté';
                connectionStatus.className = 'text-success';
                addMessage('Socket.IO connecté !', 'ai');
                console.log('✅ Socket.IO connecté');
            });
            
            socket.on('disconnect', function() {
                isConnected = false;
                connectionStatus.textContent = '❌ Déconnecté';
                connectionStatus.className = 'text-danger';
                console.log('❌ Socket.IO déconnecté');
            });
            
            socket.on('ai_response', function(data) {
                console.log('🤖 Réponse IA:', data);
                addMessage(data.message.content, 'ai');
            });
            
            socket.on('message_received', function(data) {
                console.log('📨 Message reçu:', data);
            });
            
            socket.on('error', function(error) {
                console.error('❌ Erreur Socket.IO:', error);
                connectionStatus.textContent = '❌ Erreur: ' + error.message;
                connectionStatus.className = 'text-danger';
            });
        }
        
        // Initialisation au chargement du DOM
        document.addEventListener('DOMContentLoaded', function() {
            console.log('📋 DOM chargé, initialisation...');
            
            // Test immédiat des éléments
            setTimeout(testElements, 500);
            
            // Event listeners pour les boutons
            if (sendBtn) {
                sendBtn.addEventListener('click', sendMessage);
                console.log('✅ Event listener ajouté au bouton Send');
            } else {
                console.error('❌ sendBtn non trouvé');
            }
            
            if (uploadBtn) {
                uploadBtn.addEventListener('click', showUpload);
                console.log('✅ Event listener ajouté au bouton Upload');
            } else {
                console.error('❌ uploadBtn non trouvé');
            }
            
            if (messageInput) {
                messageInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        sendMessage();
                    }
                });
                console.log('✅ Event listener ajouté à messageInput');
            } else {
                console.error('❌ messageInput non trouvé');
            }
            
            // Initialisation Socket.IO
            initSocket();
            
            // Message de bienvenue après initialisation
            setTimeout(() => {
                addMessage('Interface prête ! Testez les boutons.', 'ai');
            }, 2000);
        });
        
        // Fonctions globales pour les appels onclick
        window.sendMessage = sendMessage;
        window.showUpload = showUpload;
        window.testAlert = testAlert;
        window.testConsole = testConsole;
        window.testElements = testElements;
        
        console.log('📜 Script terminé, fonctions disponibles globalement');
    </script>
</body>
</html>'''
    
    return html_content

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload de fichier"""
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        filename = f"{timestamp}_{filename}"
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'path': file_path,
            'size': os.path.getsize(file_path)
        })
    
    return jsonify({'error': 'Type de fichier non autorisé'}), 400

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Met à jour les paramètres utilisateur"""
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({'error': 'Session non trouvée'}), 401
    
    user_session = oredmind_interface.get_user_session(session_id)
    data = request.get_json()
    
    if 'profile' in data:
        user_session['profile'] = data['profile']
    
    if 'preferences' in data:
        user_session['preferences'].update(data['preferences'])
    
    return jsonify({'success': True, 'user_session': user_session})

@app.route('/api/ollama/status')
def ollama_status():
    """Status de l'intégration Ollama"""
    if oredmind_interface.ollama:
        status = oredmind_interface.ollama.get_status()
        return jsonify(status)
    else:
        return jsonify({
            'connected': False,
            'error': 'Ollama non initialisé'
        })

@app.route('/api/ollama/models')
def ollama_models():
    """Liste des modèles Ollama"""
    if oredmind_interface.ollama and oredmind_interface.ollama.is_connected:
        models = oredmind_interface.ollama.list_models()
        return jsonify({'models': models})
    else:
        return jsonify({'models': [], 'error': 'Ollama non connecté'})

@app.route('/api/ollama/install-instructions')
def ollama_install_instructions():
    """Instructions d'installation Ollama"""
    if oredmind_interface.ollama:
        instructions = oredmind_interface.ollama.install_ollama_instructions()
        return jsonify(instructions)
    else:
        return jsonify({'error': 'Ollama non initialisé'})

# Événements SocketIO

@socketio.on('connect')
def handle_connect():
    """Connexion WebSocket"""
    session_id = session.get('session_id')
    if not session_id:
        # Créer une nouvelle session si elle n'existe pas
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        logger.info(f"🆔 Nouvelle session Socket.IO créée: {session_id}")
    
    if session_id:
        join_room(session_id)
        emit('connected', {'session_id': session_id})
        logger.info(f"🔌 Client connecté: {session_id}")
        
        # Pré-initialisation de la session utilisateur
        user_session = oredmind_interface.get_user_session(session_id)
        logger.info(f"👤 Session utilisateur Socket.IO préparée: {user_session['user_id']}")

@socketio.on('disconnect')
def handle_disconnect():
    """Déconnexion WebSocket"""
    session_id = session.get('session_id')
    if session_id:
        leave_room(session_id)
        logger.info(f"Client déconnecté: {session_id}")

@socketio.on('send_message')
def handle_message(data):
    """Traitement des messages"""
    logger.info(f"📨 Message reçu: {data}")
    session_id = session.get('session_id')
    if not session_id:
        logger.error("❌ Session non trouvée")
        emit('error', {'message': 'Session non trouvée'})
        return
    
    try:
        user_session = oredmind_interface.get_user_session(session_id)
        logger.info(f"👤 Session utilisateur trouvée: {user_session['user_id']}")
        
        # Message utilisateur
        user_message = ChatMessage(
            id=str(uuid.uuid4()),
            user_id=user_session['user_id'],
            content=data.get('message', ''),
            message_type='user',
            modality=data.get('modality', 'text'),
            timestamp=time.time(),
            attachments=data.get('attachments', [])
        )
        
        oredmind_interface.add_chat_message(session_id, user_message)
        
        # Émission du message utilisateur
        emit('message_received', {
            'message': asdict(user_message)
        }, room=session_id)
        
        # Traitement par O-RedMind
        if oredmind_interface.oredmind_core:
            logger.info("🤖 Traitement avec O-RedMind Core")
            process_with_oredmind(session_id, user_message, user_session)
        else:
            logger.info("🔄 Mode fallback activé")
            # Mode fallback
            process_with_fallback(session_id, user_message, user_session)
    
    except Exception as e:
        logger.error(f"Erreur traitement message: {e}")
        emit('error', {'message': f'Erreur: {str(e)}'})

def _build_intelligent_prompt(user_session: Dict[str, Any], personal_context: str, user_message: str, personal_memory = None) -> str:
    """Construit un prompt pour conversation naturelle et apprentissage"""
    
    # Analyse de la reconnaissance utilisateur
    is_diego = "Diego" in personal_context
    is_creator = ("OpenRed" in personal_context or "OPENRED" in personal_context)
    has_real_memory = (personal_context and personal_context != "Aucune information personnelle mémorisée.")
    
    # Instructions de base absolues
    core_identity = """Tu es O-RedMind, l'assistant IA du projet OpenRed.

RÈGLES DE CONVERSATION STRICTES :
1. RÉPONDS NATURELLEMENT comme un ami proche
2. NE TE PRÉSENTE JAMAIS (pas de "C'est O-RedMind ici" ou similaire)
3. PAS de formules de politesse répétitives
4. PAS de phrases d'au revoir ou de conclusions pompeuses
5. VARIE tes expressions - jamais la même structure de phrase
6. SOIS DIRECT ET CONCIS - pas de longs paragraphes
7. UNE SEULE IDÉE par réponse maximum"""
    
    # Gestion de l'identité utilisateur
    if has_real_memory and is_diego and is_creator:
        user_recognition = f"""
UTILISATEUR : Diego (ton créateur)
Infos connues : {personal_context}
STYLE : Conversation décontractée entre amis, tu le connais bien"""
    elif has_real_memory:
        user_recognition = f"""
UTILISATEUR CONNU : {personal_context}
STYLE : Amical mais respectueux"""
    else:
        user_recognition = """
NOUVEL UTILISATEUR
STYLE : Curieux mais discret"""
    
    # Règles conversationnelles strictes
    conversation_flow = f"""

POUR CE MESSAGE SPÉCIFIQUE "{user_message}" :
- Réponds en 1-2 phrases maximum
- AUCUNE présentation/introduction
- AUCUNE formule de politesse répétitive
- AUCUNE question multiple dans la même réponse
- Sois naturel et spontané
- Montre que tu retiens les nouvelles infos

INTERDIT ABSOLUMENT :
- "Bon Diego !" / "Bonjour Diego !" répétés
- "C'est O-RedMind ici/ici"
- "Comment ça va avec [chose] ?"
- "J'ai toujours envie d'apprendre"
- "Je te souhaite [formule]"
- Questions multiples enchainées"""
    
    return f"{core_identity}{user_recognition}{conversation_flow}"

def process_with_oredmind(session_id: str, user_message: ChatMessage, user_session: Dict[str, Any]):
    """Traite le message avec O-RedMind + Ollama"""
    try:
        # Émission du status de traitement
        socketio.emit('ai_thinking', {
            'message': '� O-RedMind + Ollama réfléchit...'
        }, room=session_id)
        
        # TRAITEMENT HYBRIDE : O-REDMIND MÉMOIRE + OLLAMA + MÉMOIRE PERSONNELLE
        logger.info(f"🧠 Système hybride complet: O-RedMind + Mémoire Personnelle + Ollama")
        
        user_id = user_session.get('user_id', f"user_{session_id}")
        
        # RECONNAISSANCE AUTOMATIQUE D'UTILISATEUR EXISTANT
        memory_path = Path.home() / ".openred" / "memory"
        existing_user_id = find_existing_user_profile(memory_path, user_message.content)
        
        if existing_user_id:
            logger.info(f"🎯 Utilisateur existant reconnu: {existing_user_id}")
            user_id = existing_user_id
            # Mise à jour de la session avec l'utilisateur reconnu
            user_session['user_id'] = user_id
        
        # RÉCUPÉRATION DE LA MÉMOIRE PERSONNELLE
        personal_memory = oredmind_interface.get_personal_memory(user_id)
        
        # EXTRACTION ET STOCKAGE DES NOUVELLES INFORMATIONS
        extracted_info = personal_memory.update_from_conversation(user_message.content)
        if extracted_info:
            logger.info(f"🧠 Nouvelles informations extraites: {extracted_info}")
        
        context = {
            'timestamp': user_message.timestamp,
            'profile': user_session['profile'],
            'session_id': session_id,
            'user_preferences': user_session['preferences'],
            'personal_memory': personal_memory.get_personal_summary()
        }
        
        # 1. APPRENTISSAGE avec O-RedMind (mémoire + analyse)
        if hasattr(oredmind_interface.oredmind_core, '_learn_private_level'):
            logger.info("📚 Phase d'apprentissage...")
            oredmind_interface.oredmind_core._learn_private_level(user_message.content, context)
        
        # 2. CONSTRUCTION DU CONTEXTE MÉMOIRE ENRICHI
        memory_context = f"[Profil: {user_session['profile']}, Préférences: {user_session['preferences']}]"
        
        # Ajout des informations personnelles
        personal_context = personal_memory.get_personal_summary()
        if personal_context:
            memory_context += f"\n\nInformations personnelles de {user_id}:\n{personal_context}"
        
        # 3. GÉNÉRATION avec Ollama enrichi par la mémoire
        logger.info("� Génération réponse avec Ollama enrichi...")
        
        # Construction du prompt système intelligent et personnalisé
        system_prompt = _build_intelligent_prompt(user_session, personal_context, user_message.content, personal_memory)
        
        if oredmind_interface.ollama and oredmind_interface.ollama.is_connected:
            ollama_response = oredmind_interface.ollama.simple_chat(
                user_message.content,
                system_prompt
            )
            
            logger.info(f"🤖 Réponse Ollama+Mémoire: {ollama_response[:100] if ollama_response else 'None'}...")
            
            if ollama_response and not ollama_response.startswith('❌'):
                # 4. SAUVEGARDE de l'interaction en mémoire
                if hasattr(oredmind_interface.oredmind_core, '_store_interaction_memory'):
                    logger.info("💾 Sauvegarde interaction en mémoire...")
                    oredmind_interface.oredmind_core._store_interaction_memory(
                        user_message.content, ollama_response, context
                    )
                
                # Succès avec O-RedMind + Ollama + Mémoire
                ai_message = ChatMessage(
                    id=str(uuid.uuid4()),
                    user_id='oredmind_hybrid',
                    content=ollama_response,
                    message_type='ai',
                    modality='text',
                    timestamp=time.time(),
                    attachments=[],
                    reasoning_type='oredmind_ollama_memory',
                    confidence=0.95
                )
                
                oredmind_interface.add_chat_message(session_id, ai_message)
                
                # Émission de la réponse
                socketio.emit('ai_response', {
                    'message': asdict(ai_message)
                }, room=session_id)
                
                logger.info("✅ Réponse hybride O-RedMind+Ollama+Mémoire envoyée")
                return
        
        logger.warning("❌ Système hybride échoué, fallback vers O-RedMind seul")
        
        # Fallback vers O-RedMind seul si Ollama échoue
        oredmind_response = oredmind_interface.oredmind_core.process_user_interaction(
            user_message.content,
            context
        )
        
        logger.info(f"🧠 Réponse O-RedMind fallback: {oredmind_response[:100] if oredmind_response else 'None'}...")
        
        if oredmind_response:
            # Succès avec O-RedMind + Mémoire
            ai_message = ChatMessage(
                id=str(uuid.uuid4()),
                user_id='oredmind_memory',
                content=oredmind_response,
                message_type='ai',
                modality='text',
                timestamp=time.time(),
                attachments=[],
                reasoning_type='oredmind_with_memory',
                confidence=0.95
            )
            
            oredmind_interface.add_chat_message(session_id, ai_message)
            
            # Émission de la réponse
            socketio.emit('ai_response', {
                'message': asdict(ai_message)
            }, room=session_id)
            
            logger.info("✅ Réponse O-RedMind avec mémoire envoyée")
            return
        
        logger.warning("❌ O-RedMind n'a pas généré de réponse, fallback vers Ollama")
        
        # Fallback vers Ollama si O-RedMind ne répond pas
        ollama_response = process_with_ollama(session_id, user_message, user_session)
        
        if ollama_response:
            # Succès avec Ollama
            ai_message = ChatMessage(
                id=str(uuid.uuid4()),
                user_id='oredmind_ollama',
                content=ollama_response,
                message_type='ai',
                modality='text',
                timestamp=time.time(),
                attachments=[],
                reasoning_type='ollama_powered',
                confidence=0.9
            )
            
            oredmind_interface.add_chat_message(session_id, ai_message)
            
            # Émission de la réponse
            socketio.emit('ai_response', {
                'message': asdict(ai_message)
            }, room=session_id)
            return
        
        # Fallback sur O-RedMind classique
        if oredmind_interface.oredmind_core:
            # Configuration du style de conversation
            style = ConversationStyle(
                formality=0.7,
                creativity=user_session['preferences'].get('creativity_level', 0.7),
                detail_level=0.8,
                empathy=0.8,
                profile_adaptation=user_session['profile']
            )
            
            # Génération de la réponse
            conversation_history = oredmind_interface.chat_history.get(session_id, [])
            recent_context = [msg.content for msg in conversation_history[-5:] if msg.message_type == 'user']
            
            response = oredmind_interface.oredmind_core.process_conversation(
                user_message.content,
                user_session['user_id'],
                user_session['profile'],
                style,
                recent_context
            )
            
            # Message de réponse
            ai_message = ChatMessage(
                id=str(uuid.uuid4()),
                user_id='oredmind',
                content=response.content,
                message_type='ai',
                modality='text',
                timestamp=time.time(),
                attachments=[],
                reasoning_type=response.reasoning_type.value if hasattr(response, 'reasoning_type') else None,
                confidence=response.confidence if hasattr(response, 'confidence') else None
            )
            
            oredmind_interface.add_chat_message(session_id, ai_message)
            
            # Émission de la réponse
            socketio.emit('ai_response', {
                'message': asdict(ai_message)
            }, room=session_id)
        else:
            # Fallback final
            process_with_fallback(session_id, user_message, user_session)
        
    except Exception as e:
        logger.error(f"Erreur O-RedMind: {e}")
        process_with_fallback(session_id, user_message, user_session)

def process_with_ollama(session_id: str, user_message: ChatMessage, user_session: Dict[str, Any]) -> Optional[str]:
    """Traitement avec Ollama"""
    try:
        logger.info(f"🦙 Tentative traitement Ollama pour: '{user_message.content}'")
        if not oredmind_interface.ollama or not oredmind_interface.ollama.is_connected:
            logger.warning("❌ Ollama non connecté")
            return None
        
        # Création du prompt système adapté au profil
        profile_prompts = {
            'Familie': "Tu es O-RedMind, l'assistant IA familial. Réponds de manière chaleureuse, bienveillante et décontractée. Utilise un ton amical et personnel.",
            'Amis': "Tu es O-RedMind, l'assistant IA entre amis. Sois décontracté, créatif et spontané. N'hésite pas à être un peu humoristique.",
            'Professionnel': "Tu es O-RedMind, l'assistant IA professionnel. Réponds de manière précise, structurée et respectueuse. Privilégie la clarté et l'efficacité.",
            'Public': "Tu es O-RedMind, l'assistant IA public. Sois diplomate, neutre et informatif. Évite les sujets controversés."
        }
        
        system_prompt = profile_prompts.get(user_session['profile'], profile_prompts['Professionnel'])
        system_prompt += f"\n\nRéponds en français. Niveau de créativité souhaité: {user_session['preferences'].get('creativity_level', 0.7)}"
        
        # Génération de la réponse avec Ollama
        logger.info(f"🤖 Génération réponse avec profil: {user_session['profile']}")
        response = oredmind_interface.ollama.simple_chat(
            user_message.content,
            system_prompt
        )
        
        logger.info(f"📤 Réponse Ollama reçue: {response[:100] if response else 'None'}...")
        
        # Vérification que la réponse n'est pas vide ou une erreur
        if response and not response.startswith('❌'):
            logger.info("✅ Réponse Ollama validée")
            return response
        else:
            logger.warning("❌ Réponse Ollama invalide ou vide")
            return None
            
    except Exception as e:
        logger.error(f"Erreur Ollama: {e}")
        return None

def process_with_fallback(session_id: str, user_message: ChatMessage, user_session: Dict[str, Any]):
    """Mode fallback sans O-RedMind"""
    try:
        # Simulation d'une réponse simple
        socketio.emit('ai_thinking', {
            'message': '🤖 Mode local activé...'
        }, room=session_id)
        
        # Réponse simple basée sur le contenu
        content = user_message.content.lower()
        
        if 'bonjour' in content or 'salut' in content:
            response_content = f"Bonjour ! Je suis O-RedMind en mode local. Comment puis-je vous aider aujourd'hui ?"
        elif 'aide' in content or 'help' in content:
            response_content = "Je peux vous aider avec diverses tâches : répondre à vos questions, analyser des documents, générer du contenu créatif, etc. Que souhaitez-vous faire ?"
        elif 'créatif' in content or 'créer' in content:
            response_content = "Je peux vous aider dans vos projets créatifs ! Souhaitez-vous que je génère du texte, des idées, ou que j'analyse du contenu créatif ?"
        else:
            response_content = f"Vous avez dit : '{user_message.content}'. Je comprends votre message et je peux vous aider à l'approfondir. Pouvez-vous me donner plus de contexte ?"
        
        ai_message = ChatMessage(
            id=str(uuid.uuid4()),
            user_id='oredmind_local',
            content=response_content,
            message_type='ai',
            modality='text',
            timestamp=time.time(),
            attachments=[],
            reasoning_type='analytical',
            confidence=0.8
        )
        
        oredmind_interface.add_chat_message(session_id, ai_message)
        
        socketio.emit('ai_response', {
            'message': asdict(ai_message)
        }, room=session_id)
        
    except Exception as e:
        logger.error(f"Erreur fallback: {e}")
        socketio.emit('error', {
            'message': 'Erreur lors du traitement de votre message'
        }, room=session_id)

@socketio.on('get_history')
def handle_get_history():
    """Récupère l'historique de chat"""
    session_id = session.get('session_id')
    if not session_id:
        emit('error', {'message': 'Session non trouvée'})
        return
    
    history = oredmind_interface.chat_history.get(session_id, [])
    emit('chat_history', {
        'messages': [asdict(msg) for msg in history]
    })

@socketio.on('clear_history')
def handle_clear_history():
    """Efface l'historique de chat"""
    session_id = session.get('session_id')
    if not session_id:
        emit('error', {'message': 'Session non trouvée'})
        return
    
    oredmind_interface.chat_history[session_id] = []
    emit('history_cleared', {'success': True})

def main():
    """Lance l'interface web O-RedMind"""
    print("🌐 O-RedMind Interface Web")
    print("=" * 40)
    print("🔗 Accès: http://localhost:5000")
    print("🔒 Mode: Local et Privé")
    print("✨ Fonctionnalités: Chat, Upload, Multimodal")
    print("📱 Compatible: Desktop et Mobile")
    print()
    
    # Vérification des templates et static
    templates_dir = Path(__file__).parent.parent.parent / "web" / "templates"
    static_dir = Path(__file__).parent.parent.parent / "web" / "static"
    
    if not templates_dir.exists():
        print(f"⚠️  Dossier templates manquant: {templates_dir}")
        print("   Création des templates de base...")
        create_basic_templates(templates_dir)
    
    if not static_dir.exists():
        print(f"⚠️  Dossier static manquant: {static_dir}")
        print("   Création des fichiers statiques de base...")
        create_basic_static(static_dir)
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Arrêt de O-RedMind Interface Web")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def create_basic_templates(templates_dir: Path):
    """Crée les templates HTML de base"""
    templates_dir.mkdir(exist_ok=True, parents=True)
    
    # Template de base
    base_template = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}O-RedMind{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css') }}" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">
                <i class="fas fa-brain"></i> O-RedMind
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="{{ url_for('chat') }}">
                    <i class="fas fa-comments"></i> Chat
                </a>
                <a class="nav-link" href="{{ url_for('settings') }}">
                    <i class="fas fa-cog"></i> Paramètres
                </a>
            </div>
        </div>
    </nav>
    
    <main class="container-fluid mt-4">
        {% block content %}{% endblock %}
    </main>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''
    
    # Page d'accueil
    index_template = '''{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-lg-8 mx-auto">
        <div class="text-center mb-5">
            <h1 class="display-4">
                <i class="fas fa-brain text-primary"></i>
                O-RedMind
            </h1>
            <p class="lead">Votre Intelligence Artificielle Personnelle et Privée</p>
        </div>
        
        <div class="row">
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-lock fa-3x text-success mb-3"></i>
                        <h5>100% Privé</h5>
                        <p>Toutes vos données restent sur votre appareil</p>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-magic fa-3x text-warning mb-3"></i>
                        <h5>Multimodal</h5>
                        <p>Texte, images, audio, code et documents</p>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-user-cog fa-3x text-info mb-3"></i>
                        <h5>Personnalisé</h5>
                        <p>S'adapte à votre style et vos préférences</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="text-center mt-5">
            <a href="{{ url_for('chat') }}" class="btn btn-primary btn-lg">
                <i class="fas fa-comments"></i> Commencer à chatter
            </a>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # Interface de chat
    chat_template = '''{% extends "base.html" %}

{% block content %}
<div class="row h-100">
    <div class="col-12">
        <div class="card h-100">
            <div class="card-header">
                <div class="row align-items-center">
                    <div class="col">
                        <h5 class="mb-0">
                            <i class="fas fa-robot"></i> 
                            O-RedMind Chat
                            <small class="text-muted">- {{ user_session.profile }}</small>
                        </h5>
                    </div>
                    <div class="col-auto">
                        <button class="btn btn-sm btn-outline-danger" onclick="clearChat()">
                            <i class="fas fa-trash"></i> Effacer
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="card-body p-0" style="height: 60vh; overflow-y: auto;" id="chatMessages">
                <!-- Messages affichés ici -->
            </div>
            
            <div class="card-footer">
                <div class="input-group">
                    <input type="text" class="form-control" id="messageInput" 
                           placeholder="Tapez votre message...">
                    <button class="btn btn-outline-secondary" type="button" onclick="showUpload()">
                        <i class="fas fa-paperclip"></i>
                    </button>
                    <button class="btn btn-primary" type="button" onclick="sendMessage()">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
                
                <input type="file" id="fileInput" style="display: none;" 
                       onchange="handleFileSelect(this)">
                       
                <div class="mt-2">
                    <small class="text-muted">
                        Mode: <span id="connectionStatus">Connexion...</span>
                    </small>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script src="{{ url_for('static', filename='js/chat.js') }}"></script>
{% endblock %}'''
    
    # Page des paramètres
    settings_template = '''{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-lg-8 mx-auto">
        <h2><i class="fas fa-cog"></i> Paramètres</h2>
        
        <div class="card mt-4">
            <div class="card-header">
                <h5>Profil Actuel</h5>
            </div>
            <div class="card-body">
                <div class="mb-3">
                    <label class="form-label">Profil de Communication</label>
                    <select class="form-select" id="profileSelect">
                        <option value="Familie">Familie</option>
                        <option value="Amis">Amis</option>
                        <option value="Professionnel">Professionnel</option>
                        <option value="Public">Public</option>
                    </select>
                </div>
            </div>
        </div>
        
        <div class="card mt-4">
            <div class="card-header">
                <h5>Préférences IA</h5>
            </div>
            <div class="card-body">
                <div class="mb-3">
                    <label class="form-label">Niveau de Créativité</label>
                    <input type="range" class="form-range" id="creativityRange" 
                           min="0" max="1" step="0.1" value="0.7">
                    <div class="form-text">0 = Factuel, 1 = Très créatif</div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">Longueur des Réponses</label>
                    <select class="form-select" id="lengthSelect">
                        <option value="short">Courtes</option>
                        <option value="medium" selected>Moyennes</option>
                        <option value="long">Détaillées</option>
                    </select>
                </div>
            </div>
        </div>
        
        <div class="mt-4">
            <button class="btn btn-success" onclick="saveSettings()">
                <i class="fas fa-save"></i> Sauvegarder
            </button>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script src="{{ url_for('static', filename='js/settings.js') }}"></script>
{% endblock %}'''
    
    # Écriture des fichiers
    with open(templates_dir / "base.html", 'w', encoding='utf-8') as f:
        f.write(base_template)
    
    with open(templates_dir / "index.html", 'w', encoding='utf-8') as f:
        f.write(index_template)
    
    with open(templates_dir / "chat.html", 'w', encoding='utf-8') as f:
        f.write(chat_template)
    
    with open(templates_dir / "settings.html", 'w', encoding='utf-8') as f:
        f.write(settings_template)
    
    print(f"✅ Templates créés dans {templates_dir}")

def create_basic_static(static_dir: Path):
    """Crée les fichiers statiques de base"""
    static_dir.mkdir(exist_ok=True, parents=True)
    (static_dir / "css").mkdir(exist_ok=True)
    (static_dir / "js").mkdir(exist_ok=True)
    
    # CSS personnalisé
    css_content = '''/* O-RedMind Custom Styles */

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f8f9fa;
}

.navbar-brand {
    font-weight: bold;
}

.chat-message {
    margin-bottom: 1rem;
    padding: 0.75rem;
    border-radius: 0.5rem;
}

.chat-message.user {
    background-color: #007bff;
    color: white;
    text-align: right;
    margin-left: 20%;
}

.chat-message.ai {
    background-color: #e9ecef;
    color: #333;
    margin-right: 20%;
}

.chat-message.system {
    background-color: #fff3cd;
    color: #856404;
    text-align: center;
    font-style: italic;
}

.thinking {
    opacity: 0.7;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% { opacity: 0.7; }
    50% { opacity: 1; }
    100% { opacity: 0.7; }
}

.status-online {
    color: #28a745;
}

.status-offline {
    color: #dc3545;
}

.file-attachment {
    background-color: #f8f9fa;
    border: 1px dashed #dee2e6;
    border-radius: 0.375rem;
    padding: 0.5rem;
    margin-top: 0.5rem;
}

.confidence-badge {
    font-size: 0.75rem;
    margin-left: 0.5rem;
}

.reasoning-type {
    font-size: 0.75rem;
    opacity: 0.7;
    margin-top: 0.25rem;
}'''
    
    # JavaScript principal
    js_app_content = '''// O-RedMind App JavaScript

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
}'''
    
    # JavaScript pour le chat
    js_chat_content = '''// O-RedMind Chat JavaScript

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
    if (confirm('Êtes-vous sûr de vouloir effacer tout l\'historique ?')) {
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
}'''
    
    # JavaScript pour les paramètres
    js_settings_content = '''// O-RedMind Settings JavaScript

document.addEventListener('DOMContentLoaded', function() {
    loadSettings();
});

function loadSettings() {
    // Charger les paramètres depuis la session
    // TODO: Implémenter le chargement des paramètres
}

function saveSettings() {
    const profile = document.getElementById('profileSelect').value;
    const creativity = parseFloat(document.getElementById('creativityRange').value);
    const responseLength = document.getElementById('lengthSelect').value;
    
    const settings = {
        profile: profile,
        preferences: {
            creativity_level: creativity,
            response_length: responseLength
        }
    };
    
    fetch('/api/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Paramètres sauvegardés', 'success');
        } else {
            showNotification('Erreur sauvegarde: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        showNotification('Erreur: ' + error.message, 'danger');
    });
}'''
    
    # Écriture des fichiers
    with open(static_dir / "css" / "style.css", 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    with open(static_dir / "js" / "app.js", 'w', encoding='utf-8') as f:
        f.write(js_app_content)
    
    with open(static_dir / "js" / "chat.js", 'w', encoding='utf-8') as f:
        f.write(js_chat_content)
    
    with open(static_dir / "js" / "settings.js", 'w', encoding='utf-8') as f:
        f.write(js_settings_content)
    
    print(f"✅ Fichiers statiques créés dans {static_dir}")

if __name__ == "__main__":
    main()