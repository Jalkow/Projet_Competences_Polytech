from flask import Flask, request, jsonify
import os
import json

from recup_data_matrice_croisees import extract_infos_matrices
from recup_data_referentiels_powerpoint import extract_infos_competences
from recup_data_programme import extract_infos_programme
from recup_all_data import extract_all_formation_data

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs_scrapping")
DATA_DIR = os.path.join(BASE_DIR, "Documents_competences")

@app.route("/programme/<formation>/<mode_formation>")
def programme(formation, mode_formation):
    formation_dir = os.path.join(OUTPUT_DIR, formation)

    # crée le dir si jamais il existe pas sinon ne fait rien
    os.makedirs(formation_dir) 

    programme_scrapped_data_json = os.path.join(formation_dir, "programme_output.json")

    if os.path.exists(programme_scrapped_data_json):
        with open(programme_scrapped_data_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)

    else:
        PROGRAMMES_DIR = os.path.join(DATA_DIR, "programmes")
        programme_file = os.path.join(PROGRAMMES_DIR, f"programme_{formation}.pdf")

        if(os.path.exists(programme_file)):
            # cela crée le fichier en même temps que récupérant données
            result = extract_infos_programme(programme_file, mode_formation)
    
            return jsonify(result)
        
        # si fichier programme n'existe pas -> erreur pas possible d'avoir les données du programme de la formation donnée
        else:
            return jsonify({
                "error": f"Fichier programme introuvable pour la formation '{formation}'"
            }), 404


@app.route("/matrice/<formation>")
def matrice(formation):
    formation_dir = os.path.join(OUTPUT_DIR, formation)

    # crée le dir si jamais il existe pas sinon ne fait rien
    os.makedirs(formation_dir, exist_ok=True)

    matrice_scrapped_data_json = os.path.join(formation_dir, "matrice_output.json")

    if os.path.exists(matrice_scrapped_data_json):
        with open(matrice_scrapped_data_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    else:
        MATRICES_DIR = os.path.join(DATA_DIR, "matrices_croisees")
        matrice_file_path = os.path.join(MATRICES_DIR, f"matrice_croisee_{formation}.xlsx")

        if os.path.exists(matrice_file_path):
            # cela crée le fichier en même temps que récupérant données
            result = extract_infos_matrices(matrice_file_path)

            return jsonify(result)
        
        # si fichier excel matrice croisee n'existe pas -> erreur pas possible d'avoir les données de la matrice croisee de la formation donnée
        else:
            return jsonify({
                "error": f"Fichier matrice croisee introuvable pour la formation : '{formation}'"
            }), 404


@app.route("/referentiel/<formation>")
def referentiel(formation):
    formation_dir = os.path.join(OUTPUT_DIR, formation)

    # crée le dir si jamais il existe pas sinon ne fait rien
    os.makedirs(formation_dir, exist_ok=True)

    referentiel_scrapped_data_json = os.path.join(formation_dir, "referentiel_output.json")

    if os.path.exists(referentiel_scrapped_data_json):
        with open(referentiel_scrapped_data_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    else:
        REFERENTIELS_DIR = os.path.join(DATA_DIR, "referentiels_APC")

        referentiel_file_path = os.path.join(REFERENTIELS_DIR, f"referentiel_{formation}.pptx")
        if os.path.exists(referentiel_file_path):
            # cela crée le fichier en même temps que récupérant données
            result = extract_infos_competences(referentiel_file_path)
            return jsonify(result)
        else:
            return jsonify({
                "error": f"Fichier référentiel introuvable pour la formation : '{formation}'"
            }), 404

@app.route("/all_infos/<formation>/<mode_formation>")
def all_infos(formation, mode_formation):
    formation_dir = os.path.join(OUTPUT_DIR, formation)

    # crée le dir si jamais il existe pas sinon ne fait rien
    os.makedirs(formation_dir, exist_ok=True)

    all_scrapped_data_json = os.path.join(formation_dir, f"all_data.json")

    if os.path.exists(all_scrapped_data_json):
        with open(all_scrapped_data_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    
    else:
        # crée tous les fichiers json nécessaire pour avoir le fichier avec toutes les datas + le fichier json avec toutes les datas
        result = extract_all_formation_data(formation, mode_formation, DATA_DIR, formation_dir)

        # si le fichier contenant toute les données n'a pas pu être créé -> retour erreur
        if(result["data"] is None):
            return jsonify({
                "error": result["erreur"]
            }), 404

        # fichier a été créé correctement
        return jsonify(result["data"])


if __name__ == "__main__":
    app.run(debug=True)