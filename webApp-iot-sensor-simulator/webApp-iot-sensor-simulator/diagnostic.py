#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de diagnostic pour le projet IoT.
"""

import sys
import importlib

# Liste des modules à vérifier
modules = [
    "flask",
    "flask_cors",
    "flask_socketio",
    "paho.mqtt.client"
]

print("== Diagnostic du projet IoT ==")
print(f"Python version: {sys.version}")
print("Vérification des modules...")

for module_name in modules:
    try:
        module = importlib.import_module(module_name)
        print(f"✅ {module_name} - OK (version: {getattr(module, '__version__', 'inconnue')})")
        
        # Vérification spécifique pour paho.mqtt
        if module_name == "paho.mqtt.client":
            print(f"   - API versions disponibles: {dir(module.CallbackAPIVersion)}")
    except ImportError:
        print(f"❌ {module_name} - ÉCHEC: Module non trouvé")
    except Exception as e:
        print(f"❌ {module_name} - ÉCHEC: {str(e)}")

print("\nVérification des chemins Python:")
for path in sys.path:
    print(f"- {path}")

print("\nTerminé.")
