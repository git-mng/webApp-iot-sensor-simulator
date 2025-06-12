#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simulateur de capteurs pour bâtiments scolaires.
Ce script génère des données sur l'état et l'occupation des bâtiments
scolaires et les publie sur un topic MQTT.
"""

import json
import random
import time
import uuid
import datetime
from paho.mqtt import client as mqtt_client
import sys
import os

# Ajout du répertoire parent au path pour importer config.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BROKER_ADRESSE, BROKER_PORT, CLIENT_ID_BASE, TOPIC_BATIMENTS, INTERVALLE_BATIMENTS

# Liste des bâtiments à simuler
BATIMENTS = [
    {
        "nom": "Bâtiment Sciences",
        "salles": [
            {"nom": "Salle S101", "fonction": "Laboratoire Physique", "capacite": 30},
            {"nom": "Salle S102", "fonction": "Laboratoire Chimie", "capacite": 25},
            {"nom": "Salle S201", "fonction": "Salle de Cours", "capacite": 40},
            {"nom": "Salle S202", "fonction": "Salle Informatique", "capacite": 20}
        ]
    },
    {
        "nom": "Bâtiment Lettres",
        "salles": [
            {"nom": "Salle L101", "fonction": "Salle de Cours", "capacite": 45},
            {"nom": "Salle L102", "fonction": "Bibliothèque", "capacite": 50},
            {"nom": "Salle L201", "fonction": "Salle de Séminaire", "capacite": 30}
        ]
    },
    {
        "nom": "Bâtiment Administration",
        "salles": [
            {"nom": "Salle A101", "fonction": "Bureau Administratif", "capacite": 10},
            {"nom": "Salle A102", "fonction": "Salle de Réunion", "capacite": 15},
            {"nom": "Salle A103", "fonction": "Accueil", "capacite": 5}
        ]
    }
]

def connecter_mqtt():
    """Établit une connexion au broker MQTT."""
    # Génération d'un ID client unique
    id_client = f"{CLIENT_ID_BASE}batiment_{str(uuid.uuid4())[:8]}"
    
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

def generer_horaires():
    """Génère des horaires d'ouverture et de fermeture réalistes."""
    jour_actuel = datetime.datetime.now().weekday()
    
    # Weekend (samedi=5, dimanche=6)
    if jour_actuel >= 5:
        # Certains bâtiments sont fermés le weekend
        if random.random() < 0.7:  # 70% de chance d'être fermé
            return {
                "est_ouvert": False,
                "heure_ouverture": None,
                "heure_fermeture": None
            }
        else:
            # Horaires réduits le weekend
            heure_ouverture = f"{random.randint(9, 10)}:00"
            heure_fermeture = f"{random.randint(14, 16)}:00"
    else:
        # Jours de semaine
        heure_ouverture = f"{random.randint(7, 9)}:00"
        heure_fermeture = f"{random.randint(17, 20)}:00"
    
    # Déterminer si le bâtiment est actuellement ouvert
    heure_actuelle = datetime.datetime.now().time()
    heure_ouv = datetime.datetime.strptime(heure_ouverture, "%H:%M").time()
    heure_ferm = datetime.datetime.strptime(heure_fermeture, "%H:%M").time()
    est_ouvert = heure_ouv <= heure_actuelle <= heure_ferm
    
    return {
        "est_ouvert": est_ouvert,
        "heure_ouverture": heure_ouverture,
        "heure_fermeture": heure_fermeture
    }

def generer_donnees_salle(salle):
    """Génère des données pour une salle spécifique."""
    # Déterminer si la salle est occupée
    est_occupee = random.random() < 0.6  # 60% de chance d'être occupée pendant les heures d'ouverture
    
    if est_occupee:
        occupation = random.randint(1, salle["capacite"])
    else:
        occupation = 0
    
    temperature = round(random.uniform(19.0, 25.0), 1)  # Température en °C
    
    return {
        "nom": salle["nom"],
        "fonction": salle["fonction"],
        "capacite": salle["capacite"],
        "occupation_actuelle": occupation,
        "est_occupee": est_occupee,
        "temperature": temperature
    }

def generer_donnees_batiment(batiment):
    """Génère des données pour un bâtiment entier."""
    horaires = generer_horaires()
    salles_donnees = []
    
    # Si le bâtiment est fermé, toutes les salles sont inoccupées
    if not horaires["est_ouvert"]:
        for salle in batiment["salles"]:
            salle_data = {
                "nom": salle["nom"],
                "fonction": salle["fonction"],
                "capacite": salle["capacite"],
                "occupation_actuelle": 0,
                "est_occupee": False,
                "temperature": round(random.uniform(17.0, 20.0), 1)  # Température plus basse si fermé
            }
            salles_donnees.append(salle_data)
    else:
        for salle in batiment["salles"]:
            salles_donnees.append(generer_donnees_salle(salle))
    
    return {
        "nom": batiment["nom"],
        "est_ouvert": horaires["est_ouvert"],
        "heure_ouverture": horaires["heure_ouverture"],
        "heure_fermeture": horaires["heure_fermeture"],
        "salles": salles_donnees,
        "timestamp": time.time()
    }

def publier(client):
    """Publie périodiquement les données de tous les bâtiments."""
    while True:
        try:
            for batiment in BATIMENTS:
                donnees = generer_donnees_batiment(batiment)
                message = json.dumps(donnees, ensure_ascii=False)
                topic = f"{TOPIC_BATIMENTS}/{batiment['nom'].replace(' ', '_').lower()}"
                result = client.publish(topic, message)
                
                # Vérification de la publication
                statut = result[0]
                if statut == 0:
                    print(f"Message envoyé au topic {topic}")
                else:
                    print(f"Échec d'envoi du message au topic {topic}")
                
                # Petit délai entre chaque bâtiment
                time.sleep(1)
                
            # Attente avant la prochaine série de publications
            time.sleep(INTERVALLE_BATIMENTS)
            
        except Exception as e:
            print(f"Erreur: {e}")
            time.sleep(5)  # Attente en cas d'erreur avant de réessayer

def executer():
    """Fonction principale du simulateur."""
    client = connecter_mqtt()
    client.loop_start()
    publier(client)

if __name__ == '__main__':
    print("Démarrage du simulateur de capteurs de bâtiments scolaires...")
    executer()
