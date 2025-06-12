#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API REST pour accéder aux données des capteurs IoT.
Ce script s'abonne aux topics MQTT, stocke les données et les expose via une API REST.
"""

import json
import time
import uuid
import threading
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt_client
from config import *

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('api_rest')

# Initialisation de l'application Flask
app = Flask(__name__)
CORS(app)  # Active CORS pour permettre les requêtes cross-origin
socketio = SocketIO(app, cors_allowed_origins="*")

# Dictionnaire pour stocker les dernières données reçues
donnees_capteurs = {
    "parking": {},
    "batiments": {},
    "wifi": {},
    "meteo": {},
    "transport": {
        "bus": {},
        "taxi": {}
    }
}

# Dictionnaire pour stocker l'historique des données
historique_donnees = {
    "parking": {},
    "batiments": {},
    "wifi": {},
    "meteo": {},
    "transport": {
        "bus": {},
        "taxi": {}
    }
}

# Verrou pour protéger l'accès aux données
verrou_donnees = threading.Lock()

def connecter_mqtt():
    """Établit une connexion au broker MQTT."""
    # Génération d'un ID client unique
    id_client = f"{CLIENT_ID_BASE}{str(uuid.uuid4())[:8]}"
    
    def au_connexion(client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"Connecté au broker MQTT! ID client: {id_client}")
            # S'abonner à tous les topics définis dans la configuration
            for topic in TOPICS:
                client.subscribe(topic)
                logger.info(f"Abonné au topic: {topic}")
        else:
            logger.error(f"Échec de connexion au broker MQTT, code retour {rc}")
    
    def au_message(client, userdata, msg):
        """Callback appelé à la réception d'un message MQTT."""
        try:
            # Décoder le message JSON
            payload = json.loads(msg.payload.decode())
            topic = msg.topic
            
            # Traiter le message selon le topic
            if topic.startswith("iot/parking/"):
                with verrou_donnees:
                    parking_id = topic.split("/")[-1]
                    donnees_capteurs["parking"][parking_id] = payload
                    
                    # Ajouter à l'historique
                    if parking_id not in historique_donnees["parking"]:
                        historique_donnees["parking"][parking_id] = []
                    historique_donnees["parking"][parking_id].append({
                        "timestamp": payload.get("timestamp", time.time()),
                        "places_disponibles": payload.get("places_disponibles", 0)
                    })
                    
                    # Émettre un événement WebSocket
                    socketio.emit('update_parking', payload)
            
            elif topic.startswith("iot/batiments/"):
                with verrou_donnees:
                    batiment_id = topic.split("/")[-1]
                    donnees_capteurs["batiments"][batiment_id] = payload
                    
                    # Ajouter à l'historique (occupation totale)
                    if batiment_id not in historique_donnees["batiments"]:
                        historique_donnees["batiments"][batiment_id] = []
                    
                    # Calculer l'occupation totale
                    occupation_totale = 0
                    for salle in payload.get("salles", []):
                        occupation_totale += salle.get("occupation_actuelle", 0)
                    
                    historique_donnees["batiments"][batiment_id].append({
                        "timestamp": payload.get("timestamp", time.time()),
                        "occupation_totale": occupation_totale
                    })
                    
                    # Émettre un événement WebSocket
                    socketio.emit('update_batiment', payload)
            
            elif topic.startswith("iot/wifi/"):
                with verrou_donnees:
                    wifi_id = topic.split("/")[-1]
                    donnees_capteurs["wifi"][wifi_id] = payload
                    
                    # Ajouter à l'historique
                    if wifi_id not in historique_donnees["wifi"]:
                        historique_donnees["wifi"][wifi_id] = []
                    historique_donnees["wifi"][wifi_id].append({
                        "timestamp": payload.get("timestamp", time.time()),
                        "puissance_signal": payload.get("puissance_signal", 0),
                        "utilisateurs_connectes": payload.get("utilisateurs_connectes", 0)
                    })
                    
                    # Émettre un événement WebSocket
                    socketio.emit('update_wifi', payload)
            
            elif topic.startswith("iot/meteo/"):
                with verrou_donnees:
                    meteo_id = topic.split("/")[-1]
                    donnees_capteurs["meteo"][meteo_id] = payload
                    
                    # Ajouter à l'historique
                    if meteo_id not in historique_donnees["meteo"]:
                        historique_donnees["meteo"][meteo_id] = []
                    historique_donnees["meteo"][meteo_id].append({
                        "timestamp": payload.get("timestamp", time.time()),
                        "temperature": payload.get("temperature", 0),
                        "humidite": payload.get("humidite", 0)
                    })
                    
                    # Émettre un événement WebSocket
                    socketio.emit('update_meteo', payload)
            
            elif topic.startswith("iot/transport/position/bus/"):
                with verrou_donnees:
                    bus_id = topic.split("/")[-1]
                    donnees_capteurs["transport"]["bus"][bus_id] = payload
                    
                    # Ajouter à l'historique (position uniquement)
                    if bus_id not in historique_donnees["transport"].get("bus", {}):
                        historique_donnees["transport"]["bus"][bus_id] = []
                    historique_donnees["transport"]["bus"][bus_id].append({
                        "timestamp": payload.get("timestamp", time.time()),
                        "latitude": payload.get("latitude", 0),
                        "longitude": payload.get("longitude", 0),
                        "passagers": payload.get("passagers", 0)
                    })
                    
                    # Émettre un événement WebSocket
                    socketio.emit('update_transport_bus', payload)
            
            elif topic.startswith("iot/transport/position/taxi/"):
                with verrou_donnees:
                    taxi_id = topic.split("/")[-1]
                    donnees_capteurs["transport"]["taxi"][taxi_id] = payload
                    
                    # Ajouter à l'historique (position uniquement)
                    if taxi_id not in historique_donnees["transport"].get("taxi", {}):
                        historique_donnees["transport"]["taxi"][taxi_id] = []
                    historique_donnees["transport"]["taxi"][taxi_id].append({
                        "timestamp": payload.get("timestamp", time.time()),
                        "latitude": payload.get("latitude", 0),
                        "longitude": payload.get("longitude", 0),
                        "disponible": payload.get("disponible", False)
                    })
                    
                    # Émettre un événement WebSocket
                    socketio.emit('update_transport_taxi', payload)
            
        except json.JSONDecodeError:
            logger.error(f"Erreur de décodage JSON pour le message sur le topic {msg.topic}")
        except Exception as e:
            logger.error(f"Erreur lors du traitement du message MQTT: {e}")
    
    # Création du client MQTT
    client = mqtt_client.Client(client_id=id_client, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION1)
    client.on_connect = au_connexion
    client.on_message = au_message
    
    # Connexion au broker
    try:
        client.connect(BROKER_ADRESSE, BROKER_PORT)
        return client
    except Exception as e:
        logger.error(f"Erreur lors de la connexion au broker MQTT: {e}")
        return None

def nettoyer_donnees_anciennes():
    """Nettoie les données plus anciennes que DUREE_CONSERVATION."""
    while True:
        try:
            temps_actuel = time.time()
            seuil_temps = temps_actuel - DUREE_CONSERVATION
            
            with verrou_donnees:
                # Nettoyage des données historiques pour le parking
                for parking_id in list(historique_donnees["parking"].keys()):
                    historique_donnees["parking"][parking_id] = [
                        d for d in historique_donnees["parking"][parking_id]
                        if d["timestamp"] >= seuil_temps
                    ]
                
                # Nettoyage des données historiques pour les bâtiments
                for batiment_id in list(historique_donnees["batiments"].keys()):
                    historique_donnees["batiments"][batiment_id] = [
                        d for d in historique_donnees["batiments"][batiment_id]
                        if d["timestamp"] >= seuil_temps
                    ]
                
                # Nettoyage des données historiques pour le WiFi
                for wifi_id in list(historique_donnees["wifi"].keys()):
                    historique_donnees["wifi"][wifi_id] = [
                        d for d in historique_donnees["wifi"][wifi_id]
                        if d["timestamp"] >= seuil_temps
                    ]
                
                # Nettoyage des données historiques pour la météo
                for meteo_id in list(historique_donnees["meteo"].keys()):
                    historique_donnees["meteo"][meteo_id] = [
                        d for d in historique_donnees["meteo"][meteo_id]
                        if d["timestamp"] >= seuil_temps
                    ]
                
                # Nettoyage des données historiques pour les bus
                for bus_id in list(historique_donnees["transport"]["bus"].keys()):
                    historique_donnees["transport"]["bus"][bus_id] = [
                        d for d in historique_donnees["transport"]["bus"][bus_id]
                        if d["timestamp"] >= seuil_temps
                    ]
                
                # Nettoyage des données historiques pour les taxis
                for taxi_id in list(historique_donnees["transport"]["taxi"].keys()):
                    historique_donnees["transport"]["taxi"][taxi_id] = [
                        d for d in historique_donnees["transport"]["taxi"][taxi_id]
                        if d["timestamp"] >= seuil_temps
                    ]
            
            logger.info("Nettoyage des données anciennes effectué")
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des données anciennes: {e}")
        
        # Attendre jusqu'au prochain nettoyage
        time.sleep(PERIODE_NETTOYAGE)

# Routes de l'API REST

@app.route('/api/status', methods=['GET'])
def get_status():
    """Retourne le statut de l'API."""
    return jsonify({
        "status": "en ligne",
        "timestamp": time.time()
    })

@app.route('/api/parking', methods=['GET'])
def get_parking():
    """Retourne les données de tous les parkings."""
    with verrou_donnees:
        return jsonify(donnees_capteurs["parking"])

@app.route('/api/parking/<id>', methods=['GET'])
def get_parking_by_id(id):
    """Retourne les données d'un parking spécifique."""
    with verrou_donnees:
        if id in donnees_capteurs["parking"]:
            return jsonify(donnees_capteurs["parking"][id])
        else:
            return jsonify({"erreur": "Parking non trouvé"}), 404

@app.route('/api/parking/<id>/historique', methods=['GET'])
def get_parking_history(id):
    """Retourne l'historique des données d'un parking spécifique."""
    with verrou_donnees:
        if id in historique_donnees["parking"]:
            # Filtrer selon les paramètres de requête
            debut = request.args.get('debut', None)
            fin = request.args.get('fin', None)
            
            donnees = historique_donnees["parking"][id]
            
            if debut:
                debut = float(debut)
                donnees = [d for d in donnees if d["timestamp"] >= debut]
            
            if fin:
                fin = float(fin)
                donnees = [d for d in donnees if d["timestamp"] <= fin]
            
            return jsonify(donnees)
        else:
            return jsonify({"erreur": "Historique du parking non trouvé"}), 404

@app.route('/api/batiments', methods=['GET'])
def get_batiments():
    """Retourne les données de tous les bâtiments."""
    with verrou_donnees:
        return jsonify(donnees_capteurs["batiments"])

@app.route('/api/batiments/<id>', methods=['GET'])
def get_batiment_by_id(id):
    """Retourne les données d'un bâtiment spécifique."""
    with verrou_donnees:
        if id in donnees_capteurs["batiments"]:
            return jsonify(donnees_capteurs["batiments"][id])
        else:
            return jsonify({"erreur": "Bâtiment non trouvé"}), 404

@app.route('/api/batiments/<id>/historique', methods=['GET'])
def get_batiment_history(id):
    """Retourne l'historique des données d'un bâtiment spécifique."""
    with verrou_donnees:
        if id in historique_donnees["batiments"]:
            # Filtrer selon les paramètres de requête
            debut = request.args.get('debut', None)
            fin = request.args.get('fin', None)
            
            donnees = historique_donnees["batiments"][id]
            
            if debut:
                debut = float(debut)
                donnees = [d for d in donnees if d["timestamp"] >= debut]
            
            if fin:
                fin = float(fin)
                donnees = [d for d in donnees if d["timestamp"] <= fin]
            
            return jsonify(donnees)
        else:
            return jsonify({"erreur": "Historique du bâtiment non trouvé"}), 404

@app.route('/api/wifi', methods=['GET'])
def get_wifi():
    """Retourne les données de tous les points d'accès WiFi."""
    with verrou_donnees:
        return jsonify(donnees_capteurs["wifi"])

@app.route('/api/wifi/<id>', methods=['GET'])
def get_wifi_by_id(id):
    """Retourne les données d'un point d'accès WiFi spécifique."""
    with verrou_donnees:
        if id in donnees_capteurs["wifi"]:
            return jsonify(donnees_capteurs["wifi"][id])
        else:
            return jsonify({"erreur": "Point d'accès WiFi non trouvé"}), 404

@app.route('/api/wifi/<id>/historique', methods=['GET'])
def get_wifi_history(id):
    """Retourne l'historique des données d'un point d'accès WiFi spécifique."""
    with verrou_donnees:
        if id in historique_donnees["wifi"]:
            # Filtrer selon les paramètres de requête
            debut = request.args.get('debut', None)
            fin = request.args.get('fin', None)
            
            donnees = historique_donnees["wifi"][id]
            
            if debut:
                debut = float(debut)
                donnees = [d for d in donnees if d["timestamp"] >= debut]
            
            if fin:
                fin = float(fin)
                donnees = [d for d in donnees if d["timestamp"] <= fin]
            
            return jsonify(donnees)
        else:
            return jsonify({"erreur": "Historique du point d'accès WiFi non trouvé"}), 404

@app.route('/api/meteo', methods=['GET'])
def get_meteo():
    """Retourne les données de toutes les stations météo."""
    with verrou_donnees:
        return jsonify(donnees_capteurs["meteo"])

@app.route('/api/meteo/<id>', methods=['GET'])
def get_meteo_by_id(id):
    """Retourne les données d'une station météo spécifique."""
    with verrou_donnees:
        if id in donnees_capteurs["meteo"]:
            return jsonify(donnees_capteurs["meteo"][id])
        else:
            return jsonify({"erreur": "Station météo non trouvée"}), 404

@app.route('/api/meteo/<id>/historique', methods=['GET'])
def get_meteo_history(id):
    """Retourne l'historique des données d'une station météo spécifique."""
    with verrou_donnees:
        if id in historique_donnees["meteo"]:
            # Filtrer selon les paramètres de requête
            debut = request.args.get('debut', None)
            fin = request.args.get('fin', None)
            
            donnees = historique_donnees["meteo"][id]
            
            if debut:
                debut = float(debut)
                donnees = [d for d in donnees if d["timestamp"] >= debut]
            
            if fin:
                fin = float(fin)
                donnees = [d for d in donnees if d["timestamp"] <= fin]
            
            return jsonify(donnees)
        else:
            return jsonify({"erreur": "Historique de la station météo non trouvé"}), 404

@app.route('/api/transport/bus', methods=['GET'])
def get_bus():
    """Retourne les données de tous les bus."""
    with verrou_donnees:
        return jsonify(donnees_capteurs["transport"]["bus"])

@app.route('/api/transport/bus/<id>', methods=['GET'])
def get_bus_by_id(id):
    """Retourne les données d'un bus spécifique."""
    with verrou_donnees:
        if id in donnees_capteurs["transport"]["bus"]:
            return jsonify(donnees_capteurs["transport"]["bus"][id])
        else:
            return jsonify({"erreur": "Bus non trouvé"}), 404

@app.route('/api/transport/taxi', methods=['GET'])
def get_taxi():
    """Retourne les données de tous les taxis."""
    with verrou_donnees:
        return jsonify(donnees_capteurs["transport"]["taxi"])

@app.route('/api/transport/taxi/<id>', methods=['GET'])
def get_taxi_by_id(id):
    """Retourne les données d'un taxi spécifique."""
    with verrou_donnees:
        if id in donnees_capteurs["transport"]["taxi"]:
            return jsonify(donnees_capteurs["transport"]["taxi"][id])
        else:
            return jsonify({"erreur": "Taxi non trouvé"}), 404

def demarrer_api():
    """Fonction principale pour démarrer l'API REST."""
    # Connexion au broker MQTT
    client_mqtt = connecter_mqtt()
    if client_mqtt is None:
        logger.error("Impossible de démarrer l'API: échec de connexion au broker MQTT")
        return
    
    # Démarrer la boucle MQTT dans un thread séparé
    client_mqtt.loop_start()
    
    # Démarrer le thread de nettoyage des données anciennes
    thread_nettoyage = threading.Thread(target=nettoyer_donnees_anciennes)
    thread_nettoyage.daemon = True
    thread_nettoyage.start()
    
    # Démarrer le serveur Flask avec Socket.IO
    logger.info(f"Démarrage de l'API REST sur {API_HOST}:{API_PORT}")
    socketio.run(app, host=API_HOST, port=API_PORT, debug=False, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    demarrer_api()
