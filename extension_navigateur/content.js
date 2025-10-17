/**
 * 🔗 OpenRed Protocol Handler - Content Script
 * 
 * Intercepte les clics sur les liens orp:// dans les pages web
 */

(function() {
  'use strict';
  
  console.log('🌐 OpenRed Content Script chargé');
  
  /**
   * Intercepte les clics sur les liens orp://
   */
  function interceptOrpLinks() {
    document.addEventListener('click', async function(event) {
      const target = event.target;
      
      // Vérifie si c'est un lien orp://
      if (target.tagName === 'A' && target.href && target.href.startsWith('orp://')) {
        event.preventDefault();
        event.stopPropagation();
        
        const orpUrl = target.href;
        console.log('🔗 Clic intercepté sur lien orp://', orpUrl);
        
        // Affiche un indicateur de chargement
        showLoadingIndicator(target);
        
        try {
          // Demande la résolution au background script
          const response = await chrome.runtime.sendMessage({
            type: 'RESOLVE_ORP_URL',
            url: orpUrl
          });
          
          if (response.success && response.resolvedUrl) {
            // Navigue vers l'URL résolue
            window.location.href = response.resolvedUrl;
          } else {
            // Affiche l'erreur
            showErrorMessage(target, 'Impossible de résoudre cette adresse orp://');
          }
          
        } catch (error) {
          console.error('❌ Erreur résolution orp://', error);
          showErrorMessage(target, error.message);
        } finally {
          hideLoadingIndicator(target);
        }
      }
    }, true);
  }
  
  /**
   * Améliore l'affichage des liens orp://
   */
  function enhanceOrpLinks() {
    const orpLinks = document.querySelectorAll('a[href^="orp://"]');
    
    orpLinks.forEach(link => {
      // Ajoute une classe CSS pour styling
      link.classList.add('orp-link');
      
      // Ajoute une icône OpenRed
      if (!link.querySelector('.orp-icon')) {
        const icon = document.createElement('span');
        icon.className = 'orp-icon';
        icon.textContent = '🌐';
        icon.style.marginRight = '4px';
        link.insertBefore(icon, link.firstChild);
      }
      
      // Ajoute un tooltip
      if (!link.title) {
        link.title = 'Lien OpenRed P2P - ' + link.href;
      }
    });
  }
  
  /**
   * Détecte automatiquement les URLs orp:// dans le texte
   */
  function autoDetectOrpUrls() {
    const textNodes = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT,
      null,
      false
    );
    
    const orpRegex = /orp:\/\/[^\s<>"']+/g;
    const nodes = [];
    
    let node;
    while (node = textNodes.nextNode()) {
      if (node.nodeValue.match(orpRegex)) {
        nodes.push(node);
      }
    }
    
    nodes.forEach(textNode => {
      const parent = textNode.parentNode;
      if (parent.tagName === 'A') return; // Déjà un lien
      
      const newHTML = textNode.nodeValue.replace(orpRegex, (match) => {
        return `<a href="${match}" class="auto-detected-orp-link">${match}</a>`;
      });
      
      if (newHTML !== textNode.nodeValue) {
        const wrapper = document.createElement('span');
        wrapper.innerHTML = newHTML;
        parent.replaceChild(wrapper, textNode);
      }
    });
  }
  
  /**
   * Affiche un indicateur de chargement
   */
  function showLoadingIndicator(element) {
    const indicator = document.createElement('span');
    indicator.className = 'orp-loading';
    indicator.textContent = ' ⏳';
    indicator.style.color = '#007acc';
    element.appendChild(indicator);
  }
  
  /**
   * Masque l'indicateur de chargement
   */
  function hideLoadingIndicator(element) {
    const indicator = element.querySelector('.orp-loading');
    if (indicator) {
      indicator.remove();
    }
  }
  
  /**
   * Affiche un message d'erreur
   */
  function showErrorMessage(element, message) {
    const error = document.createElement('span');
    error.className = 'orp-error';
    error.textContent = ' ❌ ' + message;
    error.style.color = '#cc0000';
    error.style.fontSize = '0.8em';
    element.appendChild(error);
    
    // Supprime le message après 5 secondes
    setTimeout(() => {
      error.remove();
    }, 5000);
  }
  
  /**
   * Injecte les styles CSS pour les liens orp://
   */
  function injectStyles() {
    const style = document.createElement('style');
    style.textContent = `
      .orp-link, .auto-detected-orp-link {
        color: #007acc !important;
        text-decoration: underline !important;
        cursor: pointer !important;
        position: relative !important;
      }
      
      .orp-link:hover, .auto-detected-orp-link:hover {
        color: #005999 !important;
        background-color: rgba(0, 122, 204, 0.1) !important;
      }
      
      .orp-link::before, .auto-detected-orp-link::before {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #007acc, #00cc88);
        opacity: 0.7;
      }
      
      .orp-loading {
        animation: orp-pulse 1s infinite;
      }
      
      @keyframes orp-pulse {
        0% { opacity: 0.5; }
        50% { opacity: 1; }
        100% { opacity: 0.5; }
      }
    `;
    document.head.appendChild(style);
  }
  
  /**
   * Initialisation
   */
  function init() {
    // Injecte les styles
    injectStyles();
    
    // Configure les intercepteurs
    interceptOrpLinks();
    
    // Améliore les liens existants
    enhanceOrpLinks();
    
    // Détection automatique
    autoDetectOrpUrls();
    
    // Observer pour les modifications DOM
    const observer = new MutationObserver((mutations) => {
      let needsUpdate = false;
      
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList') {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE) {
              if (node.tagName === 'A' && node.href && node.href.startsWith('orp://')) {
                needsUpdate = true;
              } else if (node.querySelector && node.querySelector('a[href^="orp://"]')) {
                needsUpdate = true;
              }
            }
          });
        }
      });
      
      if (needsUpdate) {
        enhanceOrpLinks();
        autoDetectOrpUrls();
      }
    });
    
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
    
    console.log('✅ OpenRed Content Script initialisé');
  }
  
  // Démarre quand le DOM est prêt
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  
})();