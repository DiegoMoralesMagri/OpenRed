// O-RedMind Settings JavaScript

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
}