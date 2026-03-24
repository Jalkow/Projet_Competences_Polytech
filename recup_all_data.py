from recup_data_matrice_croisees import extract_infos_matrices
from recup_data_referentiels_powerpoint import extract_infos_competences
from recup_data_programme import extract_infos_programme

import os
import json

def extract_all_formation_data(diminutif_formation, type_formation, documents_folder_path, output_folder_path):
    REFERENTIELS_DIR = os.path.join(documents_folder_path, "referentiels_APC")
    MATRICES_DIR = os.path.join(documents_folder_path, "matrices_croisees")
    PROGRAMMES_DIR = os.path.join(documents_folder_path, "programmes")
    diminutif_formation = diminutif_formation.lower()

    powerpoint_competences_path = os.path.join(REFERENTIELS_DIR, f"referentiel_{diminutif_formation}.pptx")
    matrice_path = os.path.join(MATRICES_DIR, f"matrice_croisee_{diminutif_formation}.xlsx")
    programme_path = os.path.join(PROGRAMMES_DIR, f"programme_{diminutif_formation}.pdf")

    if (not os.path.exists(powerpoint_competences_path)):
        return {
            "data": None, 
            "erreur": f"Il n'est pas possible de récupérer toutes les données de la formation '{diminutif_formation}' car le fichier de referentiel n'existe pas"
        }
    
    if (not os.path.exists(matrice_path)):
        return {
            "data": None, 
            "erreur": f"Il n'est pas possible de récupérer toutes les données de la formation '{diminutif_formation}' car le fichier de matrice croisees n'existe pas"
        }
    
    if (not os.path.exists(programme_path)):
        return {
            "data": None, 
            "erreur": f"Il n'est pas possible de récupérer toutes les données de la formation '{diminutif_formation}' car le fichier du programme de la formation n'existe pas"
        }

    infos_powerpoint_competences = extract_infos_competences(powerpoint_competences_path, output_folder_path)
    infos_matrice_croisee = extract_infos_matrices(matrice_path, output_folder_path)
    infos_programme = extract_infos_programme(programme_path, type_formation, output_folder_path)

    ############################################################
    # début données en partant de referentiel et UEs depuis fichier matrice
    ##############################################################

    all_infos_formation = {
        "liste_UE": infos_matrice_croisee["liste_UE"],
        "liste_competences" : [infos_comp for infos_comp in infos_powerpoint_competences.values()]
    }


    ##############################
    # combinaison données matrice
    #############################

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
    
    ##############################
    # combinaison données programme
    ##############################
    for UE in all_infos_formation["liste_UE"]:
        code_UE = UE["code"]
        
        # infos_programme : dict avec clé qui est code UE et intérieur nom UE + modules de l'UE
        if(code_UE in infos_programme):
            UE["liste_modules"] = infos_programme[code_UE]["liste_modules"]
        else:
            UE["liste_modules"] = []

    # création du fichier json avec les données scrappées
    output_file_path = os.path.join(output_folder_path, "all_data.json")
    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump(all_infos_formation, f, ensure_ascii=False, indent=4)
    
    return {"data": all_infos_formation}
        

