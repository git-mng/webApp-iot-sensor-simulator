#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simulateur de capteurs pour l'état du Wi-Fi.
Ce script génère des données sur l'état des points d'accès Wi-Fi
et les publie sur un topic MQTT.
"""

import json
import random
import time
import uuid
from paho.mqtt import client as mqtt_client
import sys
import os

# Ajout du répertoire parent au path pour importer config.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BROKER_ADRESSE, BROKER_PORT, CLIENT_ID_BASE, TOPIC_WIFI, INTERVALLE_WIFI

# Liste des points d'accès Wi-Fi à simuler
POINTS_ACCES = [
    {"id": "AP001", "nom": "WiFi-BatimentSciences-RDC", "localisation": "Bâtiment Sciences, Rez-de-chaussée"},
    {"id": "AP002", "nom": "WiFi-BatimentSciences-1erEtage", "localisation": "Bâtiment Sciences, 1er étage"},
    {"id": "AP003", "nom": "WiFi-BatimentLettres-RDC", "localisation": "Bâtiment Lettres, Rez-de-chaussée"},
    {"id": "AP004", "nom": "WiFi-BatimentLettres-1erEtage", "localisation": "Bâtiment Lettres, 1er étage"},
    {"id": "AP005", "nom": "WiFi-Administration", "localisation": "Bâtiment Administration"},
    {"id": "AP006", "nom": "WiFi-Bibliotheque", "localisation": "Bibliothèque"},
    {"id": "AP007", "nom": "WiFi-Cafeteria", "localisation": "Cafétéria"}
]

def connecter_mqtt():
    """Établit une connexion au broker MQTT."""
    # Génération d'un ID client unique
    id_client = f"{CLIENT_ID_BASE}wifi_{str(uuid.uuid4())[:8]}"
    
    def au_connexion(client, userdata, flags, rc):
        if rc == 0:
            print(f"Connecté au broker MQTT! ID client: {id_client}")
        else:
            print(f"Échec de connexion, code retour {rc}")
    
    # Création du client MQTT
    client = mqtt_client.Client(client_id=id_client, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION1)
    client.on_connect = au_connexion
    client.connect(BROKER_ADRESSE, BROKER_PORT)
    return client

def generer_donnees_wifi(point_acces):
    """Génère des données aléatoires pour un point d'accès Wi-Fi."""
    # Probabilité que le point d'accès soit en ligne (95% du temps)
    est_en_ligne = random.random() < 0.95
    
    if est_en_ligne:
        # Générer une puissance de signal réaliste
        puissance_signal = random.randint(60, 100)  # En pourcentage
        
        # Simuler le nombre d'utilisateurs connectés
        heure_actuelle = time.localtime().tm_hour
        if 8 <= heure_actuelle <= 18:  # Heures de cours
            utilisateurs_connectes = random.randint(5, 50)
        else:  # En dehors des heures de cours
            utilisateurs_connectes = random.randint(0, 15)
        
        # Simuler la bande passante utilisée (en Mbps)
        bande_passante_utilisee = round(random.uniform(1.0, 100.0), 2)
        
        # Calculer un niveau de congestion (0-100%)
        niveau_congestion = min(100, int(utilisateurs_connectes * 2 + bande_passante_utilisee / 2))
    else:
        puissance_signal = 0
        utilisateurs_connectes = 0
        bande_passante_utilisee = 0.0
        niveau_congestion = 0
    
    return {
        "id": point_acces["id"],
        "nom": point_acces["nom"],
        "localisation": point_acces["localisation"],
        "est_en_ligne": est_en_ligne,
        "puissance_signal": puissance_signal,
        "utilisateurs_connectes": utilisateurs_connectes,
        "bande_passante_utilisee": bande_passante_utilisee,
        "niveau_congestion": niveau_congestion,
        "timestamp": time.time()
    }

def publier(client):
    """Publie périodiquement les données de tous les points d'accès Wi-Fi."""
    while True:
        try:
            for point_acces in POINTS_ACCES:
                donnees = generer_donnees_wifi(point_acces)
                message = json.dumps(donnees, ensure_ascii=False)
                topic = f"{TOPIC_WIFI}/{point_acces['id']}"
                result = client.publish(topic, message)
                
                # Vérification de la publication
                statut = result[0]
                if statut == 0:
                    print(f"Message envoyé au topic {topic}")
                else:
                    print(f"Échec d'envoi du message au topic {topic}")
                
                # Petit délai entre chaque point d'accès
                time.sleep(0.5)
                
            # Attente avant la prochaine série de publications
            time.sleep(INTERVALLE_WIFI)
            
        except Exception as e:
            print(f"Erreur: {e}")
            time.sleep(5)  # Attente en cas d'erreur avant de réessayer

def executer():
    """Fonction principale du simulateur."""
    client = connecter_mqtt()
    client.loop_start()
    publier(client)

if __name__ == '__main__':
    print("Démarrage du simulateur de capteurs Wi-Fi...")
    executer()
