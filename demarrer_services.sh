#!/bin/bash

# Script pour démarrer tous les services IoT

# Répertoire de base du projet
PROJET_DIR="$HOME/projet_iot"

# Fonction pour arrêter tous les services en cas d'interruption
function arreter_services {
    echo "Arrêt des services..."
    
    # Arrêter les simulateurs
    if [ -n "$PID_SIMULATEURS" ]; then
        kill $PID_SIMULATEURS
    fi
    
    # Arrêter l'API REST
    if [ -n "$PID_API" ]; then
        kill $PID_API
    fi
    
    # Arrêter le serveur web
    if [ -n "$PID_WEB" ]; then
        kill $PID_WEB
    fi
    
    exit 0
}

# Capturer les signaux d'interruption
trap arreter_services SIGINT SIGTERM

# Créer un répertoire pour les logs
mkdir -p "$PROJET_DIR/logs"

echo "Démarrage des services IoT..."

# 1. Démarrer les simulateurs de capteurs
echo "Démarrage des simulateurs..."
python3 "$PROJET_DIR/demarrer_simulateurs.py" > "$PROJET_DIR/logs/simulateurs.log" 2>&1 &
PID_SIMULATEURS=$!
echo "Simulateurs démarrés avec PID $PID_SIMULATEURS"

# Attendre que les simulateurs soient prêts
sleep 5

# 2. Démarrer l'API REST
echo "Démarrage de l'API REST..."
cd "$PROJET_DIR/api"
python3 app.py > "$PROJET_DIR/logs/api.log" 2>&1 &
PID_API=$!
echo "API REST démarrée avec PID $PID_API"

# Attendre que l'API soit prête
sleep 5

# 3. Démarrer un serveur web simple pour la dashboard
echo "Démarrage du serveur web pour la dashboard..."
cd "$PROJET_DIR/dashboard"

# Utiliser Python pour créer un serveur web simple
python3 -m http.server 8080 > "$PROJET_DIR/logs/web.log" 2>&1 &
PID_WEB=$!
echo "Serveur web démarré avec PID $PID_WEB"

echo "Tous les services sont démarrés!"
echo "Dashboard accessible à l'adresse: http://localhost:8080"
echo "API REST accessible à l'adresse: http://localhost:5000/api"
echo ""
echo "Logs disponibles dans $PROJET_DIR/logs/"
echo "Appuyez sur Ctrl+C pour arrêter tous les services"

# Maintenir le script en cours d'exécution
wait
