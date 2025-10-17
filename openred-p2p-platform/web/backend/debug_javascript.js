
            // Variables globales
            let myPhantoms = [];
            let systemStats = {};
            let projectionWebSocket = null;

            // FONCTIONS PRINCIPALES (définies avant DOM)
            
            // Charger mes phantoms Enhanced
            async function loadMyPhantoms() {
                console.log('Chargement Phantoms Enhanced...');
                try {
                    const response = await fetch('/api/images/my-urns', {
                        credentials: 'include'
                    });

                    if (response.ok) {
                        const data = await response.json();
                        myPhantoms = data.phantoms || [];
                        displayMyPhantoms();
                        console.log('Phantoms charges:', myPhantoms.length);
                    } else {
                        console.warn('Erreur chargement phantoms:', response.status);
                        const container = document.getElementById('myPhantomsList');
                        if (container) {
                            container.innerHTML = '<p>Erreur chargement phantoms Enhanced</p>';
                        }
                    }
                } catch (error) {
                    console.error('Erreur chargement phantoms:', error);
                    const container = document.getElementById('myPhantomsList');
                    if (container) {
                        container.innerHTML = '<p>Erreur connexion Enhanced</p>';
                    }
                }
            }

            // Afficher projections actives Enhanced
            function showActiveStreams() {
                console.log('Affichage projections actives Enhanced...');
                const projectionsSection = document.getElementById('projectionsSection');
                if (projectionsSection) {
                    if (projectionsSection.style.display === 'none' || !projectionsSection.style.display) {
                        projectionsSection.style.display = 'block';
                        loadActiveProjections();
                    } else {
                        projectionsSection.style.display = 'none';
                    }
                } else {
                    console.warn('Section projections non trouvee');
                    alert('Projections Enhanced - La section projections sera bientot disponible!');
                }
            }

            // Connecter serveur de projection Enhanced
            function connectProjectionServer() {
                console.log('Connexion serveur projection Enhanced...');
                alert('Serveur de Projection Enhanced\n\nStatus: Actif sur port 8002\nType: Phoenix de Schrodinger WebSocket\nSecurite: NCK + Verification continue\nEnhanced: Projection ORP temporaire uniquement\n\nURL: http://localhost:8002\n\nAucune image complete n est jamais reconstituee!');
            }

            // Charger projections actives Enhanced
            async function loadActiveProjections() {
                try {
                    console.log('Chargement projections actives...');
                    const response = await fetch('/api/images/active-projections', {
                        credentials: 'include'
                    });

                    const container = document.getElementById('activeProjections');
                    if (response.ok) {
                        const data = await response.json();
                        const projections = data.projections || [];
                        
                        if (container) {
                            if (projections.length === 0) {
                                container.innerHTML = '<p>Aucune projection Enhanced active</p>';
                            } else {
                                container.innerHTML = projections.map(proj => `
                                    <div class="phantom-card">
                                        <h4>Phoenix ${proj.phantom_id}</h4>
                                        <p>Viewers: ${proj.viewers}</p>
                                        <p>Demarre: ${new Date(proj.started_at).toLocaleString()}</p>
                                        <button onclick="stopProjection('${proj.phantom_id}')">Arreter</button>
                                    </div>
                                `).join('');
                            }
                        }
                    } else {
                        if (container) {
                            container.innerHTML = '<p>Erreur chargement projections Enhanced</p>';
                        }
                    }
                } catch (error) {
                    console.error('Erreur projections Enhanced:', error);
                    const container = document.getElementById('activeProjections');
                    if (container) {
                        container.innerHTML = '<p>Erreur connexion projections Enhanced</p>';
                    }
                }
            }

            // Initialisation Enhanced
            document.addEventListener('DOMContentLoaded', function() {
                console.log('[INIT] Initialisation Enhanced Phantom URN Interface');
                
                // Vérifier authentification
                checkAuthStatus();
                
                setupUpload();
                loadStats();
                loadMyPhantoms();  // Changé de loadMyImages() à loadMyPhantoms()
                
                // Actualiser toutes les 30 secondes
                setInterval(() => {
                    loadStats();
                    if (document.getElementById('projectionsSection').style.display !== 'none') {
                        showActiveStreams();
                    }
                }, 30000);
                
                console.log('[OK] Interface Enhanced initialisée');
            });

            // Vérification statut authentification
            async function checkAuthStatus() {
                try {
                    console.log('[AUTH] Vérification authentification...');
                    const response = await fetch('/api/phantom/status', {
                        credentials: 'include'
                    });
                    console.log('[AUTH] Statut auth:', response.status);
                    if (!response.ok && response.status === 401) {
                        console.warn('[ERROR] Non authentifié');
                        alert('[WARNING] Veuillez vous connecter pour utiliser l interface Enhanced');
                    } else {
                        console.log('[OK] Authentifié');
                    }
                } catch (error) {
                    console.error('[ERROR] Erreur vérification auth:', error);
                }
            }

            // Configuration upload
            function setupUpload() {
                const uploadArea = document.getElementById('uploadArea');
                const fileInput = document.getElementById('fileInput');

                // Drag & Drop
                uploadArea.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    uploadArea.classList.add('dragover');
                });

                uploadArea.addEventListener('dragleave', () => {
                    uploadArea.classList.remove('dragover');
                });

                uploadArea.addEventListener('drop', (e) => {
                    e.preventDefault();
                    uploadArea.classList.remove('dragover');
                    handleFiles(e.dataTransfer.files);
                });

                // File input Enhanced
                fileInput.addEventListener('change', (e) => {
                    console.log('📁 Fichier sélectionné:', e.target.files);
                    handleFiles(e.target.files);
                });

                // Click upload area Enhanced
                uploadArea.addEventListener('click', () => {
                    console.log('[CLICK] Click zone upload');
                    fileInput.click();
                });
            }

            // Gestion fichiers Enhanced
            function handleFiles(files) {
                console.log('[FILES] Traitement fichiers:', files.length);
                Array.from(files).forEach(file => {
                    console.log('[FILE] Fichier:', file.name, file.type, file.size);
                    if (file.type.startsWith('image/')) {
                        console.log('[OK] Image valide, début upload Enhanced...');
                        uploadImage(file);
                    } else {
                        console.warn('[ERROR] Type fichier non supporté:', file.type);
                        alert('[WARNING] Seules les images sont supportées: ' + file.name);
                    }
                });
            }

            // Upload image et burn en Phantom URN Enhanced
            async function uploadImage(file) {
                console.log('[BURN] Début upload Enhanced:', file.name);
                
                const formData = new FormData();
                formData.append('file', file);

                try {
                    console.log('[UPLOAD] Envoi vers /api/images/upload...');
                    const response = await fetch('/api/images/upload', {
                        method: 'POST',
                        credentials: 'include',
                        body: formData
                    });

                    console.log('[RESPONSE] Réponse serveur:', response.status);

                    if (response.ok) {
                        const result = await response.json();
                        console.log('[OK] Résultat Enhanced:', result);
                        
                        alert(`[PHOENIX] Phoenix de Schrödinger créé!
                        
[URN] Phantom ID: ${result.phantom_id}
[ATOMIC] Fragments atomiques: ${result.total_fragments}
[KEY] NCK System: Activé
[OK] Vérification continue: Active
[PHOENIX] État quantique: Crypté

Système dual Enhanced:
• [ORP] ORP: ${result.dual_system?.orp_streaming || 'Actif'}
• [URN] URN: ${result.dual_system?.urn_download || 'Fragments cryptés'}`);
                        
                        loadMyPhantoms();
                        loadStats();
                    } else {
                        console.error('[ERROR] Erreur réponse:', response.status);
                        const error = await response.json();
                        console.error('[ERROR] Détails erreur:', error);
                        alert('[ERROR] Erreur upload Enhanced: ' + (error.detail || 'Erreur inconnue'));
                    }
                } catch (error) {
                    console.error('[ERROR] Erreur upload Enhanced:', error);
                    alert('[ERROR] Erreur upload Enhanced: ' + error.message);
                }
            }

            // Charger statistiques
            async function loadStats() {
                try {
                    const response = await fetch('/api/images/system-stats', {
                        credentials: 'include'
                    });

                    if (response.ok) {
                        const data = await response.json();
                        systemStats = data.stats;
                        displayStats();
                    }
                } catch (error) {
                    console.error('Erreur stats:', error);
                }
            }

            // Afficher statistiques Phantom URN
            function displayStats() {
                const statsContainer = document.getElementById('stats');
                
                const fragmentation = systemStats.fragmentation || {};
                const projectionServer = systemStats.projection_server || {};
                
                statsContainer.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-number">${systemStats.active_phantoms || 0}</div>
                        <div>Phantoms Actifs</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${systemStats.total_fragments || 0}</div>
                        <div>Fragments Atomiques</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${projectionServer.active_connections || 0}</div>
                        <div>Connexions ORP</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${fragmentation.atomic_pixels ? '[OK]' : '[ERROR]'}</div>
                        <div>Fragmentation Atomique</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${fragmentation.cryptographic_chaining ? '[OK]' : '[ERROR]'}</div>
                        <div>Chaînage Cryptographique</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${fragmentation.physical_storage ? '[WARNING]' : '🔒'}</div>
                        <div>Stockage Physique</div>
                    </div>`;
            }

            // Charger mes phantoms
            async function loadMyPhantoms() {
                try {
                    const response = await fetch('/api/images/my-urns', {
                        credentials: 'include'
                    });

                    if (response.ok) {
                        const data = await response.json();
                        myPhantoms = data.phantoms;
                        displayMyPhantoms();
                    }
                } catch (error) {
                    console.error('Erreur phantoms:', error);
                }
            }

            // Afficher mes phantoms
            function displayMyPhantoms() {
                const container = document.getElementById('myPhantoms');
                
                if (myPhantoms.length === 0) {
                    container.innerHTML = '<p>Aucun Phantom URN. Uploadez votre première image pour la fragmentation atomique!</p>';
                    return;
                }

                container.innerHTML = myPhantoms.map(phantom => `
                    <div class="image-card">
                        <div class="image-info">
                            <h4>� ${phantom.phantom_id}</h4>
                            <p><strong>Dimensions:</strong> ${phantom.dimensions[0]}x${phantom.dimensions[1]}</p>
                            <p><strong>Fragments atomiques:</strong> ${phantom.total_fragments}</p>
                            <p><strong>Type:</strong> 
                                <span class="stream-indicator">[PROJECTION] Projection ORP</span> 
                                <span class="download-indicator">� URN Fragmentée</span>
                            </p>
                            <p><strong>Streaming:</strong> ${phantom.streaming_url}</p>
                            <p><strong>WebSocket:</strong> ${phantom.websocket_url}</p>
                            <div style="margin-top: 10px;">
                                <button class="btn" onclick="startPhantomProjection('${phantom.phantom_id}')">[PROJECTION] Projection ORP</button>
                                ${img.type !== 'stream' ? 
                                    '<button class="btn" onclick="generateDownloadToken(\''+img.urn_id+'\')">💾 Token DL</button>' : ''
                                }
                                <button class="btn btn-secondary" onclick="showUrnInfo(\''+img.urn_id+'\')">ℹ️ Info</button>
                                <button class="btn" onclick="startPhantomProjection('${phantom.phantom_id}')">[PROJECTION] Projection ORP</button>
                                <button class="btn btn-secondary" onclick="enableURNDownload('${phantom.phantom_id}')">[URN] Activer URN</button>
                                <button class="btn btn-secondary" onclick="viewPhantomInfo('${phantom.phantom_id}')">[FILES] Info</button>
                            </div>
                        </div>
                    </div>
                `).join('');
            }

            // Démarrer projection phantom
            async function startPhantomProjection(phantomId) {
                try {
                    const response = await fetch(`/api/images/start-stream/${phantomId}`, {
                        method: 'POST',
                        credentials: 'include',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({mode: 'projection'})
                    });

                    if (response.ok) {
                        const result = await response.json();
                        alert(`[PROJECTION] Projection ORP configurée!
                        
Phantom ID: ${result.phantom_id}
WebSocket: ${result.streaming_info.websocket_url}
HTTP: ${result.streaming_info.http_endpoint}
Protocol: ${result.streaming_info.protocol}
Dimensions: ${result.streaming_info.dimensions.join('x')}
Fragments: ${result.streaming_info.total_fragments}`);
                        loadStats();
                    } else {
                        const error = await response.json();
                        alert('[ERROR] Erreur projection: ' + error.detail);
                    }
                } catch (error) {
                    alert('[ERROR] Erreur projection: ' + error.message);
                }
            }

            // Activer téléchargement URN
            async function enableURNDownload(phantomId) {
                try {
                    const response = await fetch(`/api/phantom/${phantomId}/enable-urn-download`, {
                        method: 'POST',
                        credentials: 'include'
                    });

                    if (response.ok) {
                        const result = await response.json();
                        alert(`[URN] URN téléchargeable activée!
                        
Phantom ID: ${result.phantom_id}
Token de téléchargement: ${result.download_token}
Message: ${result.message}

Fragments atomiques maintenant disponibles pour téléchargement.`);
                    } else {
                        const error = await response.json();
                        alert('[ERROR] Erreur activation URN: ' + error.detail);
                    }
                } catch (error) {
                    alert('[ERROR] Erreur activation URN: ' + error.message);
                }
            }

            // Voir informations phantom
            async function viewPhantomInfo(phantomId) {
                try {
                    const response = await fetch(`/api/phantom/${phantomId}/orp`, {
                        credentials: 'include'
                    });

                    if (response.ok) {
                        const result = await response.json();
                        const orp = result.orp_info;
                        alert(`[ORP] Informations Phantom URN
                        
Phantom ID: ${result.phantom_id}
Type: ${orp.type}
Description: ${orp.description}

Streaming URL: ${orp.streaming_url}
Projection: ${orp.projection_endpoint}

Système dual opérationnel!`);
                    } else {
                        const error = await response.json();
                        alert('[ERROR] Erreur info: ' + error.detail);
                    }
                } catch (error) {
                    alert('[ERROR] Erreur info: ' + error.message);
                }
            }

            // Connexion serveur projection
            function connectProjectionServer() {
                if (projectionWebSocket && projectionWebSocket.readyState === WebSocket.OPEN) {
                    alert('Déjà connecté au serveur de projection ORP!');
                    return;
                }

                try {
                    projectionWebSocket = new WebSocket('ws://localhost:8002/ws');
                    
                    projectionWebSocket.onopen = function() {
                        alert('[OK] Connecté au serveur de projection ORP!');
                    };
                    
                    projectionWebSocket.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        console.log('Message ORP:', data);
                        
                        if (data.type === 'phantom_list') {
                            console.log(`[STREAM] ${data.count} phantoms disponibles pour projection`);
                        } else if (data.type === 'phantom_projection') {
                            console.log(`[PROJECTION] Projection reçue: ${data.phantom_id}`);
                        }
                    };
                    
                    projectionWebSocket.onclose = function() {
                        console.log('Connexion ORP fermée');
                        projectionWebSocket = null;
                    };
                    
                } catch (error) {
                    alert('[ERROR] Erreur connexion ORP: ' + error.message);
                }
            }

            // Afficher info URN
            async function showUrnInfo(urnId) {
                try {
                    const response = await fetch(`/api/images/urn-info/${urnId}`, {
                        credentials: 'include'
                    });

                    if (response.ok) {
                        const data = await response.json();
                        const info = data.urn_info;
                        
                        alert(`[FILES] Informations URN\n\n` +
                              `🆔 ID: ${info.urn_id}\n` +
                              `📁 Fichier: ${info.filename}\n` +
                              `📊 Taille: ${(info.size / 1024).toFixed(1)} KB\n` +
                              `📐 Dimensions: ${info.dimensions[0]}x${info.dimensions[1]}\n` +
                              `📅 Upload: ${new Date(info.upload_time * 1000).toLocaleString()}\n` +
                              `🔒 Accès: ${info.access_level}\n` +
                              `[RESPONSE] Téléchargements: ${info.download_count}\n` +
                              `📺 Streams: ${info.stream_count}`);
                    }
                } catch (error) {
                    alert('[ERROR] Erreur info: ' + error.message);
                }
            }

            // Afficher projections actives
            function showActiveStreams() {
                const section = document.getElementById('projectionsSection');
                section.style.display = section.style.display === 'none' ? 'block' : 'none';
                
                if (section.style.display === 'block') {
                    loadActiveProjections();
                }
            }

            // Charger projections actives
            async function loadActiveProjections() {
                try {
                    const response = await fetch('/api/images/active-streams', {
                        credentials: 'include'
                    });

                    if (response.ok) {
                        const data = await response.json();
                        displayActiveProjections(data.streams);
                    }
                } catch (error) {
                    console.error('Erreur projections:', error);
                }
            }

            // Afficher projections actives
            function displayActiveProjections(streams) {
                const container = document.getElementById('activeProjections');
                
                if (streams.length === 0) {
                    container.innerHTML = '<p>Aucune projection active. Les phantoms sont prêts pour projection ORP!</p>';
                    return;
                }

                container.innerHTML = streams.map(stream => `
                    <div class="card">
                        <h4>📺 Stream ${stream.stream_id.slice(0, 16)}...</h4>
                        <p><strong>URN:</strong> ${stream.urn_id.slice(0, 20)}...</p>
                        <p><strong>Mode:</strong> ${stream.mode}</p>
                        <p><strong>Viewers:</strong> ${stream.viewer_count}</p>
                        <p><strong>Durée:</strong> ${Math.floor(stream.duration / 60)}min ${Math.floor(stream.duration % 60)}s</p>
                        <button class="btn" onclick="joinStream('${stream.stream_id}')">👀 Rejoindre</button>
                        <button class="btn btn-secondary" onclick="viewStreamData('${stream.stream_id}')">🖼️ Voir Image</button>
                    </div>
                `).join('');
            }

            // Rejoindre stream
            async function joinStream(streamId) {
                try {
                    const response = await fetch(`/api/images/join-stream/${streamId}`, {
                        method: 'POST',
                        credentials: 'include'
                    });

                    if (response.ok) {
                        alert('[OK] Stream rejoint avec succès!');
                        loadActiveStreams();
                    } else {
                        const error = await response.json();
                        alert('[ERROR] Erreur join: ' + error.detail);
                    }
                } catch (error) {
                    alert('[ERROR] Erreur join: ' + error.message);
                }
            }

            // Voir données stream
            function viewStreamData(streamId) {
                const url = `/api/images/stream-data/${streamId}`;
                window.open(url, '_blank');
            }
        