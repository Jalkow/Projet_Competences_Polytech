from recup_data_matrice_croisees import extract_infos_matrices
from recup_data_referentiels_powerpoint import extract_infos_competences

from pathlib import Path
import json

# recup que idu pour l'instant

def get_all_data_as_json(diminutif_formation):
    base_dir = Path(__file__).resolve().parent

    diminutif_formation = diminutif_formation.lower()

    powerpoint_competences_path = base_dir / "Documents_competences" / "referentiels_APC" / f"referentiel_{diminutif_formation}.pptx"
    matrice_path = base_dir / "Documents_competences" / "matrices_croisees" / f"matrice_croisee_{diminutif_formation}.xlsx"

    infos_powerpoint_competences = extract_infos_competences(powerpoint_competences_path)
    infos_matrice_croisee = extract_infos_matrices(matrice_path)

    # print(infos_powerpoint_competences)
    # print("----------------------")
    # print(infos_matrice_croisee)

    with open(f"{diminutif_formation}_output_referentiel.json", "w", encoding="utf-8") as f:
        json.dump(infos_powerpoint_competences, f, ensure_ascii=False, indent=4)

    with open(f"{diminutif_formation}_output_matrice.json", "w", encoding="utf-8") as f:
        json.dump(infos_matrice_croisee, f, ensure_ascii=False, indent=4)


    all_infos_formation = {}

        


all_infos = {
    "Formations":{}
}
get_all_data_as_json("IDU")
