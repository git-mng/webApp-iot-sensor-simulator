// Fonctions utilitaires pour l'application dashboard

/**
 * Formate une date en chaîne de caractères lisible
 * @param {number} timestamp - Timestamp Unix en secondes
 * @returns {string} Date formatée
 */
function formatDate(timestamp) {
    return moment.unix(timestamp).format('DD/MM/YYYY HH:mm:ss');
}

/**
 * Formate une heure en chaîne de caractères lisible
 * @param {number} timestamp - Timestamp Unix en secondes
 * @returns {string} Heure formatée
 */
function formatTime(timestamp) {
    return moment.unix(timestamp).format('HH:mm:ss');
}

/**
 * Met à jour l'heure de dernière mise à jour
 */
function updateLastUpdateTime() {
    document.getElementById('last-update').textContent = 'Dernière mise à jour: ' + moment().format('HH:mm:ss');
}

/**
 * Effectue une requête GET à l'API
 * @param {string} endpoint - Point de terminaison de l'API
 * @returns {Promise} Promesse contenant les données de la réponse
 */
async function fetchAPI(endpoint) {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`);
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Erreur lors de la requête API (${endpoint}):`, error);
        throw error;
    }
}

/**
 * Crée ou met à jour un graphique Chart.js
 * @param {string} canvasId - ID de l'élément canvas
 * @param {Object} config - Configuration du graphique
 * @returns {Object} Instance du graphique
 */
function createOrUpdateChart(canvasId, config) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Vérifier si un graphique existe déjà sur ce canvas
    const existingChart = Chart.getChart(canvasId);
    if (existingChart) {
        existingChart.destroy();
    }
    
    // Créer un nouveau graphique
    return new Chart(ctx, config);
}

/**
 * Obtient une couleur pour un état de remplissage
 * @param {number} percentage - Pourcentage de remplissage (0-100)
 * @returns {string} Classe CSS correspondante
 */
function getOccupancyColorClass(percentage) {
    if (percentage < 50) {
        return 'progress-low';
    } else if (percentage < 80) {
        return 'progress-medium';
    } else {
        return 'progress-high';
    }
}

/**
 * Obtient une classe d'icône pour un état météorologique
 * @param {string} weatherState - État météorologique
 * @returns {string} Classe FontAwesome correspondante
 */
function getWeatherIcon(weatherState) {
    const iconMap = {
        'Ensoleillé': 'fa-sun',
        'Partiellement nuageux': 'fa-cloud-sun',
        'Nuageux': 'fa-cloud',
        'Couvert': 'fa-cloud',
        'Brumeux': 'fa-smog',
        'Pluvieux': 'fa-cloud-rain',
        'Orageux': 'fa-bolt',
        'Neigeux': 'fa-snowflake'
    };
    
    return iconMap[weatherState] || 'fa-question';
}

/**
 * Crée un élément de carte Leaflet
 * @param {string} elementId - ID de l'élément DOM
 * @param {Array} center - Coordonnées du centre [lat, lng]
 * @param {number} zoom - Niveau de zoom
 * @returns {Object} Instance de carte Leaflet
 */
function createMap(elementId, center = CONFIG.MAP.CENTER, zoom = CONFIG.MAP.ZOOM) {
    const map = L.map(elementId).setView(center, zoom);
    
    L.tileLayer(CONFIG.MAP.TILE_LAYER, {
        attribution: CONFIG.MAP.ATTRIBUTION
    }).addTo(map);
    
    return map;
}

/**
 * Change la section active
 * @param {string} sectionId - ID de la section à afficher
 */
function changeSection(sectionId) {
    // Masquer toutes les sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Afficher la section demandée
    document.getElementById(`${sectionId}-section`).classList.add('active');
    
    // Mettre à jour le titre de la page
    const pageTitle = document.getElementById('page-title');
    switch (sectionId) {
        case 'dashboard':
            pageTitle.textContent = 'Tableau de bord';
            break;
        case 'parking':
            pageTitle.textContent = 'Parkings';
            break;
        case 'batiments':
            pageTitle.textContent = 'Bâtiments';
            break;
        case 'wifi':
            pageTitle.textContent = 'Réseau Wi-Fi';
            break;
        case 'meteo':
            pageTitle.textContent = 'Météo';
            break;
        case 'transport':
            pageTitle.textContent = 'Transports';
            break;
        default:
            pageTitle.textContent = 'Tableau de bord';
    }
    
    // Mettre à jour la navigation
    document.querySelectorAll('.sidebar-nav li').forEach(item => {
        item.classList.remove('active');
    });
    
    const activeNavItem = document.querySelector(`.sidebar-nav li a[href="#${sectionId}"]`).parentElement;
    activeNavItem.classList.add('active');
}
