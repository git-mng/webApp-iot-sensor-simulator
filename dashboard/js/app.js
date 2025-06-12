// Application principale - Point d'entrée

// Variables globales
let socket;
let refreshInterval;

/**
 * Initialise l'application
 */
function initApp() {
    // Initialiser Socket.IO
    initSocketConnection();
    
    // Initialiser les sections
    initDashboardCharts();
    initParkingSection();
    initBatimentsSection();
    initWifiSection();
    initMeteoSection();
    initTransportSection();
    
    // Configurer les gestionnaires d'événements
    setupEventHandlers();
    
    // Charger les données initiales
    refreshAllData();
    
    // Configurer le rafraîchissement automatique
    setupAutoRefresh();
}

/**
 * Initialise la connexion Socket.IO
 */
function initSocketConnection() {
    socket = io(CONFIG.SOCKET_URL);
    
    socket.on('connect', () => {
        console.log('Connecté au serveur Socket.IO');
    });
    
    socket.on('disconnect', () => {
        console.log('Déconnecté du serveur Socket.IO');
    });
    
    // Configurer les gestionnaires d'événements Socket.IO
    setupSocketEvents();
}

/**
 * Configure les gestionnaires d'événements Socket.IO
 */
function setupSocketEvents() {
    // Événements pour les mises à jour en temps réel
    socket.on('update_parking', (data) => {
        console.log('Mise à jour des données de parking reçue');
        // Mettre à jour les données si la section est active
        if (document.getElementById('parking-section').classList.contains('active')) {
            updateParkingSection();
        }
        // Toujours mettre à jour le tableau de bord
        updateDashboardMetrics();
    });
    
    socket.on('update_batiment', (data) => {
        console.log('Mise à jour des données de bâtiment reçue');
        // Mettre à jour les données si la section est active
        if (document.getElementById('batiments-section').classList.contains('active')) {
            updateBatimentsSection();
        }
        // Toujours mettre à jour le tableau de bord
        updateDashboardMetrics();
    });
    
    socket.on('update_wifi', (data) => {
        console.log('Mise à jour des données WiFi reçue');
        // Mettre à jour les données si la section est active
        if (document.getElementById('wifi-section').classList.contains('active')) {
            updateWifiSection();
        }
        // Toujours mettre à jour le tableau de bord
        updateDashboardMetrics();
    });
    
    socket.on('update_meteo', (data) => {
        console.log('Mise à jour des données météo reçue');
        // Mettre à jour les données si la section est active
        if (document.getElementById('meteo-section').classList.contains('active')) {
            updateMeteoSection();
        }
        // Toujours mettre à jour le tableau de bord
        updateDashboardMetrics();
    });
    
    socket.on('update_transport_bus', (data) => {
        console.log('Mise à jour des données de bus reçue');
        // Mettre à jour les données si la section est active
        if (document.getElementById('transport-section').classList.contains('active')) {
            updateTransportSection();
        }
        // Toujours mettre à jour le tableau de bord
        updateDashboardMetrics();
    });
    
    socket.on('update_transport_taxi', (data) => {
        console.log('Mise à jour des données de taxi reçue');
        // Mettre à jour les données si la section est active
        if (document.getElementById('transport-section').classList.contains('active')) {
            updateTransportSection();
        }
        // Toujours mettre à jour le tableau de bord
        updateDashboardMetrics();
    });
}

/**
 * Configure les gestionnaires d'événements de l'interface
 */
function setupEventHandlers() {
    // Gestionnaire pour le bouton de rafraîchissement
    document.getElementById('refresh-btn').addEventListener('click', refreshAllData);
    
    // Gestionnaires pour la navigation
    document.querySelectorAll('.sidebar-nav a').forEach(link => {
        link.addEventListener('click', (event) => {
            event.preventDefault();
            const sectionId = link.getAttribute('href').substring(1);
            changeSection(sectionId);
        });
    });
}

/**
 * Configure le rafraîchissement automatique des données
 */
function setupAutoRefresh() {
    // Effacer l'intervalle existant si nécessaire
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    
    // Configurer un nouvel intervalle
    refreshInterval = setInterval(refreshAllData, CONFIG.REFRESH_INTERVAL);
}

/**
 * Rafraîchit toutes les données
 */
function refreshAllData() {
    console.log('Rafraîchissement de toutes les données...');
    
    // Mettre à jour le tableau de bord
    updateDashboardMetrics();
    
    // Mettre à jour la section active
    const activeSection = document.querySelector('.content-section.active').id;
    
    switch (activeSection) {
        case 'dashboard-section':
            // Déjà mis à jour par updateDashboardMetrics()
            break;
        case 'parking-section':
            updateParkingSection();
            break;
        case 'batiments-section':
            updateBatimentsSection();
            break;
        case 'wifi-section':
            updateWifiSection();
            break;
        case 'meteo-section':
            updateMeteoSection();
            break;
        case 'transport-section':
            updateTransportSection();
            break;
    }
    
    // Mettre à jour l'heure de dernière mise à jour
    updateLastUpdateTime();
}

// Initialiser l'application au chargement de la page
document.addEventListener('DOMContentLoaded', initApp);
