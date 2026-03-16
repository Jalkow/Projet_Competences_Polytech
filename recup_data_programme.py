import pdfplumber
import re
import json

def extract_infos_programme(path_to_programme, formation_mode):
    modules_by_UE = {}
    current_ue = None
    current_mode = None
    correct_ue_extracted = False

    with pdfplumber.open(path_to_programme) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split("\n")

            for line in lines:
                if("alternance" in line.lower()):
                    current_mode = "alternance"


                # détecter UE (les () autour de la partie qui detecte UE et le reste sont des groups qu'on prent avec .groups() )
                UE_regex_matches = re.match(r"(UE\d{3})\s+(.*)", line)
                if UE_regex_matches:
                    code, nom = UE_regex_matches.groups()

                    current_ue = code
                    modules_by_UE[current_ue] = {
                        "nom": nom,
                        "modules": []
                    }
                    continue

                # détecter modules avec heures
                module_match = re.match(r"(.*)\s+(\d+)h\s+(\d+)h\s+(\d+)h", line)
                if module_match and current_ue:

                    nom_module, cm, td, tp = module_match.groups()

                    # ignorer modules alternance
                    if "alternance" in nom_module.lower():
                        continue

                    modules_by_UE[current_ue]["modules"].append({
                        "nom": nom_module.strip(),
                        "CM": int(cm),
                        "TD": int(td),
                        "TP": int(tp)
                    })
    
    with open(f"test_output_programme.json", "w", encoding="utf-8") as f:
        json.dump(modules_by_UE, f, ensure_ascii=False, indent=4)

