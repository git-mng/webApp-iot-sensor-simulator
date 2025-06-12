// Configuration de l'application dashboard
const CONFIG = {
    // URL de base de l'API REST
    API_BASE_URL: 'http://localhost:5000/api',
    
    // URL du serveur Socket.IO
    SOCKET_URL: 'http://localhost:5000',
    
    // Intervalle de rafraîchissement automatique en millisecondes
    REFRESH_INTERVAL: 30000, // 30 secondes
    
    // Paramètres de la carte
    MAP: {
        CENTER: [48.8566, 2.3522], // Coordonnées par défaut (Paris)
        ZOOM: 13,
        TILE_LAYER: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        ATTRIBUTION: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    },
    
    // Paramètres des graphiques
    CHART: {
        ANIMATION_DURATION: 500,
        COLORS: {
            PRIMARY: '#3498db',
            SECONDARY: '#2ecc71',
            ACCENT: '#e74c3c',
            NEUTRAL: '#95a5a6',
            SUCCESS: '#2ecc71',
            WARNING: '#f39c12',
            DANGER: '#e74c3c',
            INFO: '#3498db'
        },
        BACKGROUND_OPACITY: 0.2,
        BORDER_WIDTH: 2
    }
};
