#!/usr/bin/env python3
"""
Script pour générer une image PNG à partir d'un fichier PlantUML.
Utilise le wrapper Python plantuml.
"""

from plantuml import PlantUML
import os

# Chemin du fichier .puml
puml_file = "/home/noa/BUT2/automate/TD_UML/diagramme_complet.puml"
output_file = "/home/noa/BUT2/automate/TD_UML/diagramme_complet.png"

# Lire le contenu du fichier .puml
with open(puml_file, 'r', encoding='utf-8') as f:
    puml_code = f.read()

print(f"📊 Génération de l'image PNG...")
print(f"   Entrée  : {puml_file}")
print(f"   Sortie  : {output_file}")

try:
    # Créer une instance PlantUML avec le serveur public
    # (fallback si pas de serveur local)
    plnt = PlantUML(url='http://www.plantuml.com/plantuml/img/')
    
    # Générer l'image PNG
    png_data = plnt.processes(puml_code)
    
    # Écrire le fichier PNG
    with open(output_file, 'wb') as f:
        f.write(png_data)
    
    print(f"✅ Image PNG générée avec succès!")
    print(f"   Fichier créé : {output_file}")
    print(f"   Taille : {os.path.getsize(output_file)} bytes")
    
except Exception as e:
    print(f"❌ Erreur lors de la génération : {e}")
    print(f"   Conseil : Vérifier la connexion Internet ou utiliser un serveur PlantUML local.")

