#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simulateur de capteur pour places de parking disponibles.
Ce script génère des données fictives sur les places disponibles dans différents parkings
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
from config import BROKER_ADRESSE, BROKER_PORT, CLIENT_ID_BASE, TOPIC_PARKING, INTERVALLE_PARKING

# Liste des parkings à simuler
PARKINGS = [
    {"nom": "Parking Centre-Ville", "capacite_totale": 120},
    {"nom": "Parking Gare", "capacite_totale": 200},
    {"nom": "Parking Université", "capacite_totale": 150},
    {"nom": "Parking Centre Commercial", "capacite_totale": 300},
    {"nom": "Parking Hôpital", "capacite_totale": 80}
]

def connecter_mqtt():
    """Établit une connexion au broker MQTT."""
    # Génération d'un ID client unique
    id_client = f"{CLIENT_ID_BASE}parking_{str(uuid.uuid4())[:8]}"
    
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

def generer_donnees_parking(parking):
    """Génère des données aléatoires pour un parking."""
    capacite_totale = parking["capacite_totale"]
    # Simuler une occupation variable selon l'heure de la journée
    heure_actuelle = time.localtime().tm_hour
    
    # Facteur d'occupation basé sur l'heure (plus occupé pendant les heures de pointe)
    if 7 <= heure_actuelle <= 9 or 16 <= heure_actuelle <= 19:
        taux_occupation = random.uniform(0.7, 0.95)  # Heures de pointe: 70-95% occupé
    elif 10 <= heure_actuelle <= 15:
        taux_occupation = random.uniform(0.4, 0.8)   # Journée: 40-80% occupé
    else:
        taux_occupation = random.uniform(0.1, 0.5)   # Nuit: 10-50% occupé
    
    places_occupees = int(capacite_totale * taux_occupation)
    places_disponibles = capacite_totale - places_occupees
    
    # Ajout d'une petite variation aléatoire
    places_disponibles = max(0, places_disponibles + random.randint(-5, 5))
    
    return {
        "nom": parking["nom"],
        "capacite_totale": capacite_totale,
        "places_disponibles": places_disponibles,
        "timestamp": time.time()
    }

def publier(client):
    """Publie périodiquement les données de tous les parkings."""
    while True:
        try:
            for parking in PARKINGS:
                donnees = generer_donnees_parking(parking)
                message = json.dumps(donnees, ensure_ascii=False)
                topic = f"{TOPIC_PARKING}/{parking['nom'].replace(' ', '_').lower()}"
                result = client.publish(topic, message)
                
                # Vérification de la publication
                statut = result[0]
                if statut == 0:
                    print(f"Message envoyé au topic {topic}: {message}")
                else:
                    print(f"Échec d'envoi du message au topic {topic}")
                
                # Petit délai entre chaque parking pour éviter de surcharger le broker
                time.sleep(1)
                
            # Attente avant la prochaine série de publications
            time.sleep(INTERVALLE_PARKING)
            
        except Exception as e:
            print(f"Erreur: {e}")
            time.sleep(5)  # Attente en cas d'erreur avant de réessayer

def executer():
    """Fonction principale du simulateur."""
    client = connecter_mqtt()
    client.loop_start()
    publier(client)

if __name__ == '__main__':
    print("Démarrage du simulateur de capteurs de parking...")
    executer()
