import pdfplumber
import re
import json
import os

def extract_infos_programme(path_to_programme, formation_mode, output_folder_path):
    modules_by_UE = {}

    current_UE = None
    previous_UE = None
    first_module_after_ue_change = False
    current_module = None
    current_mode = "initial"
    stop_reading = False

    with pdfplumber.open(path_to_programme) as pdf:
        for page in pdf.pages:
            
            # si trouvé le bon programme
            if(stop_reading):
                break

            text = page.extract_text()
            lines = text.split("\n")

            for line in lines:
                UE_regex_matches = re.match(r"^(UE\d{3})\s+(.*)", line)
                    
                # si ligne signalant début des modules d'une UE :
                if(UE_regex_matches):
                    code_UE, nom_UE = UE_regex_matches.groups()
                    
                    # éviter UE du résumé du programme dans les premières pages
                    if("crédits" not in nom_UE):

                        # recupère le premier num du code de l'UE de la ligne actuelle qui est le semestre où on effectue l'UE
                        semestre_current_UE = code_UE[2]
                        # num code dernière UE visitée
                        semestre_old_UE = ""
                        if(current_UE is not None):
                            semestre_old_UE = current_UE[2]
                        
                        if(current_UE is None):
                            previous_UE = code_UE
                        else:
                            previous_UE = current_UE
                            
                        current_UE = code_UE.strip()
                        first_module_after_ue_change = True

                        # le S10 a 0 comme premier nombre donc que si ancien = 0 et nouveau est diff de 0 alors
                        # on est de retour au premier semestre de l'autre formation
                        if(semestre_old_UE != "" and (semestre_current_UE != "0" and semestre_old_UE == "0")):
                            # si le type de formation d'avant était le bon alors on a déjà toutes les bonnes infos donc on arrête de lire
                            if(current_mode == formation_mode):
                                stop_reading = True
                                break
                            
                            # sinon on change de mode
                            # initial -> alternance
                            elif(current_mode == "initial"):
                                current_mode = "alternance"
                            
                            # alternance -> initial
                            else:
                                current_mode = "initial"

                        # si bon mode et que ce n'est pas ligne du résumé au départ du document ou il y a les crédits qui sont listés
                        if(formation_mode == current_mode):
                            modules_by_UE[current_UE] = {
                                "nom": nom_UE.strip(),
                                "liste_modules" : []
                            }




                # lire les lignes d'infos des modules que si c'est le bon type de formation
                if(current_mode == formation_mode):
                    module_regex_matches = re.match(r"^(.*?)\s*\(([A-Z]+\d{3}_[A-Z]+)\s*\)", line)
                    # si ligne signalant le début de l'explication d'un module
                    if(module_regex_matches and current_UE):
                        # ajouter ancien module à la liste si il y en avait un
                        if(current_module and first_module_after_ue_change):
                            modules_by_UE[previous_UE]["liste_modules"].append(current_module)
                            first_module_after_ue_change = False
                        elif(current_module):
                            modules_by_UE[current_UE]["liste_modules"].append(current_module)

                        nom_module, code_module = module_regex_matches.groups()


                        current_module = {
                            "nom": nom_module.strip(),
                            "code": code_module,
                            "heures_TD": 0,
                            "heures_TP": 0,
                            "heures_CM": 0,
                            "heures_PTUT": 0,
                        }
                        
                    
                    # \b sers à éviter que ça match que si CM/TD sont seul caractères, pas que ça fasse partie d'un mot
                    heures_regex_matches = re.match(r"\b(CM|TD|TP|PTUT)\b.*?(\d+(?:,\d+)?)h", line)
                    if(heures_regex_matches and current_module):
                        type_h, heures = heures_regex_matches.groups()
                        heures_clean = heures.replace(",", ".").replace("h", "")
                        current_module["heures_"+type_h] = float(heures_clean)

    # création du fichier json avec les données scrappées
    output_file_path = os.path.join(output_folder_path, "programme_output.json")
    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump(modules_by_UE, f, ensure_ascii=False, indent=4)
    
    return modules_by_UE

