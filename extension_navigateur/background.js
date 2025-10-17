/**
 * 🌐 OpenRed Protocol Handler - Background Service Worker
 * 
 * Gère les requêtes orp:// et les redirige vers le résolveur P2P local
 */

// Port de communication avec le résolveur local OpenRed
const OPENRED_RESOLVER_PORT = 7888;
const OPENRED_RESOLVER_HOST = 'localhost';

// Cache des résolutions récentes
let resolutionCache = new Map();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

/**
 * Intercepte les requêtes vers orp:// et les redirige
 */
chrome.webRequest.onBeforeRequest.addListener(
  async function(details) {
    const url = details.url;
    
    // Vérifie si c'est une URL orp://
    if (url.startsWith('orp://')) {
      console.log('🔍 Interception URL orp://', url);
      
      try {
        // Résout l'URL via le résolveur P2P local
        const resolvedUrl = await resolveOrpUrl(url);
        
        if (resolvedUrl) {
          console.log('✅ URL résolue:', resolvedUrl);
          
          // Redirige vers l'URL HTTP résolue
          return { redirectUrl: resolvedUrl };
        } else {
          // Affiche une page d'erreur
          return { 
            redirectUrl: chrome.runtime.getURL('error.html') + '?url=' + encodeURIComponent(url)
          };
        }
        
      } catch (error) {
        console.error('❌ Erreur résolution orp://', error);
        return { 
          redirectUrl: chrome.runtime.getURL('error.html') + '?error=' + encodeURIComponent(error.message)
        };
      }
    }
    
    // Laisse passer les autres URLs
    return {};
  },
  { urls: ["orp://*/*"] },
  ["blocking"]
);

/**
 * Résout une URL orp:// via le résolveur P2P local
 */
async function resolveOrpUrl(orpUrl) {
  // Vérifie le cache
  const cached = resolutionCache.get(orpUrl);
  if (cached && (Date.now() - cached.timestamp) < CACHE_TTL) {
    return cached.url;
  }
  
  try {
    // Communique avec le résolveur P2P local
    const response = await fetch(`http://${OPENRED_RESOLVER_HOST}:${OPENRED_RESOLVER_PORT}/resolve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        orp_url: orpUrl,
        source: 'browser_extension'
      })
    });
    
    if (response.ok) {
      const result = await response.json();
      
      if (result.success && result.resolved_url) {
        // Met en cache
        resolutionCache.set(orpUrl, {
          url: result.resolved_url,
          timestamp: Date.now()
        });
        
        return result.resolved_url;
      }
    }
    
    return null;
    
  } catch (error) {
    console.error('❌ Erreur communication résolveur:', error);
    
    // Fallback : essaie de résoudre via méthode alternative
    return await fallbackResolve(orpUrl);
  }
}

/**
 * Méthode de fallback pour résolution
 */
async function fallbackResolve(orpUrl) {
  try {
    // Parse l'URL orp://
    const match = orpUrl.match(/^orp:\/\/([^\/]+)(\/.*)?$/);
    if (!match) return null;
    
    const fortIdentifier = match[1];
    const path = match[2] || '/';
    
    // Essaie quelques ports standards
    const standardPorts = [8080, 8081, 8082, 3000, 5000];
    
    for (const port of standardPorts) {
      try {
        const testUrl = `http://localhost:${port}${path}`;
        const response = await fetch(testUrl, { 
          method: 'HEAD',
          timeout: 2000 
        });
        
        if (response.ok) {
          console.log(`✅ Fallback réussi: ${testUrl}`);
          return testUrl;
        }
      } catch (e) {
        // Continue vers le port suivant
      }
    }
    
    return null;
    
  } catch (error) {
    console.error('❌ Erreur fallback:', error);
    return null;
  }
}

/**
 * Gestion des messages depuis le content script
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'RESOLVE_ORP_URL') {
    resolveOrpUrl(message.url)
      .then(resolvedUrl => {
        sendResponse({ success: true, resolvedUrl });
      })
      .catch(error => {
        sendResponse({ success: false, error: error.message });
      });
    
    // Indique que la réponse sera asynchrone
    return true;
  }
  
  if (message.type === 'GET_CACHE_STATS') {
    sendResponse({
      cacheSize: resolutionCache.size,
      entries: Array.from(resolutionCache.entries()).map(([url, data]) => ({
        url,
        resolvedUrl: data.url,
        timestamp: data.timestamp,
        age: Date.now() - data.timestamp
      }))
    });
  }
  
  if (message.type === 'CLEAR_CACHE') {
    resolutionCache.clear();
    sendResponse({ success: true });
  }
});

/**
 * Nettoyage périodique du cache
 */
setInterval(() => {
  const now = Date.now();
  for (const [url, data] of resolutionCache.entries()) {
    if (now - data.timestamp > CACHE_TTL) {
      resolutionCache.delete(url);
    }
  }
}, 60000); // Nettoie toutes les minutes

/**
 * Installation de l'extension
 */
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('🎉 OpenRed Protocol Handler installé !');
    
    // Ouvre la page de configuration
    chrome.tabs.create({
      url: chrome.runtime.getURL('welcome.html')
    });
  }
});

/**
 * Détection du résolveur local
 */
async function detectLocalResolver() {
  try {
    const response = await fetch(`http://${OPENRED_RESOLVER_HOST}:${OPENRED_RESOLVER_PORT}/status`);
    if (response.ok) {
      const status = await response.json();
      console.log('✅ Résolveur OpenRed détecté:', status);
      return true;
    }
  } catch (error) {
    console.log('⚠️  Résolveur OpenRed non détecté, fonctionnalité limitée');
    return false;
  }
}

// Détecte le résolveur au démarrage
detectLocalResolver();