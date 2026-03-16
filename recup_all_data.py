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


    all_infos_formation = {
        "liste_UE": infos_matrice_croisee["liste_UE"],
        "liste_competences" : [infos_comp for infos_comp in infos_powerpoint_competences.values()]
    }

    # clé = nom CE/AC et valeur = obj avec code, nom et UE liees à cette AC/CE
    dict_liaison_obj_AC_nom = {
        el["nom"].strip(): el 
        for el in infos_matrice_croisee["liens"]
        if el["code"].startswith("AC")
    }

    # mise à jour infos CE et AC
    for comp in all_infos_formation["liste_competences"]:
        
        # AC par annee
        for annee in comp["apprentissages_crit"].values():
            completed_infos_AC_list = []

            for AC_name in annee["app_list"]:
                name = AC_name.strip()

                if name in dict_liaison_obj_AC_nom:
                    completed_infos_AC_list.append(dict_liaison_obj_AC_nom[name])

            annee["app_list"] = completed_infos_AC_list
        
        
        # CE (même principe mais pas par année)
        completed_infos_CE_list = []
        dict_liaison_obj_CE_nom = {
            el["nom"].strip(): el 
            for el in infos_matrice_croisee["liens"]
            if el["code"].startswith("CE")
        }

        for CE_name in comp["composantes_essentielles"]:
            name = CE_name.strip()

            if name in dict_liaison_obj_CE_nom:
                completed_infos_CE_list.append(dict_liaison_obj_CE_nom[name])

            comp["composantes_essentielles"] = completed_infos_CE_list
    
    with open(f"{diminutif_formation}_output_all.json", "w", encoding="utf-8") as f:
        json.dump(all_infos_formation, f, ensure_ascii=False, indent=4)
        

            










        


all_infos = {
    "Formations":{}
}
get_all_data_as_json("IDU")
