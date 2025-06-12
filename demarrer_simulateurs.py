#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script principal pour démarrer tous les simulateurs de capteurs IoT.
"""

import subprocess
import time
import os
import signal
import sys

# Liste des simulateurs à démarrer
SIMULATEURS = [
    "capteurs/capteur_parking.py",
    "capteurs/capteur_batiments.py",
    "capteurs/capteur_wifi.py",
    "capteurs/capteur_meteo.py",
    "capteurs/capteur_transport.py"
]

# Liste pour stocker les processus
processus = []

def arreter_simulateurs(signal, frame):
    """Arrête proprement tous les simulateurs en cas d'interruption."""
    print("\nArrêt des simulateurs...")
    for proc in processus:
        if proc.poll() is None:  # Si le processus est toujours en cours d'exécution
            proc.terminate()
    sys.exit(0)

def main():
    """Fonction principale."""
    # Gestionnaire de signal pour arrêter proprement les simulateurs
    signal.signal(signal.SIGINT, arreter_simulateurs)
    
    print("Démarrage de tous les simulateurs de capteurs IoT...")
    
    # Démarrer chaque simulateur
    for simulateur in SIMULATEURS:
        chemin_simulateur = os.path.join(os.path.dirname(os.path.abspath(__file__)), simulateur)
        
        # S'assurer que le script est exécutable
        os.chmod(chemin_simulateur, 0o755)
        
        # Démarrer le simulateur
        try:
            proc = subprocess.Popen(
                ["python3", chemin_simulateur],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            processus.append(proc)
            print(f"Simulateur '{simulateur}' démarré avec PID {proc.pid}")
        except Exception as e:
            print(f"Erreur lors du démarrage de '{simulateur}': {e}")
    
    # Garder le programme principal en cours d'exécution
    try:
        while True:
            # Vérifier si tous les processus sont toujours en cours d'exécution
            for i, proc in enumerate(processus):
                if proc.poll() is not None:  # Le processus s'est terminé
                    print(f"Le simulateur '{SIMULATEURS[i]}' s'est arrêté avec le code {proc.returncode}")
                    # Afficher les erreurs éventuelles
                    stderr = proc.stderr.read()
                    if stderr:
                        print(f"Erreur: {stderr}")
                    
                    # Redémarrer le simulateur
                    print(f"Redémarrage du simulateur '{SIMULATEURS[i]}'...")
                    chemin_simulateur = os.path.join(os.path.dirname(os.path.abspath(__file__)), SIMULATEURS[i])
                    proc = subprocess.Popen(
                        ["python3", chemin_simulateur],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1
                    )
                    processus[i] = proc
                    print(f"Simulateur '{SIMULATEURS[i]}' redémarré avec PID {proc.pid}")
            
            # Attendre un peu avant de vérifier à nouveau
            time.sleep(5)
    except KeyboardInterrupt:
        arreter_simulateurs(None, None)

if __name__ == "__main__":
    main()
