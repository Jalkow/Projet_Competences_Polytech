from openpyxl import load_workbook
from pathlib import Path
import re

def get_color(cell_color, wb):
    """
    Retourne la couleur RGB sous forme de chaîne RRGGBB même si c'est une couleur de thème.
    """
    if cell_color is None:
        return None

    # Couleur RGB directe
    if cell_color.type == 'rgb' and cell_color.rgb:
        return cell_color.rgb[-6:]  # ignore le FF alpha

    # Couleur basée sur un thème
    if cell_color.type == 'theme' and cell_color.theme is not None:
        # wb._theme est le fichier XML du thème, openpyxl peut le résoudre
        # on peut approximer avec wb.theme_colors pour récupérer la couleur
        try:
            theme_colors = wb.theme_colors
            theme_rgb = theme_colors[cell_color.theme]
            if theme_rgb:
                return theme_rgb[-6:]
        except Exception:
            return None

    # Couleur automatique (noir)
    if cell_color.type == 'auto':
        return "000000"

    return None

def get_liaison_type(cell):
    if not cell.font or not cell.font.color:
        return None

    color = cell.font.color
    if color is None:
        return None

    if(color.type == "theme"):
        # vert 
        if(color.theme == 9):
            return "ciblee"

    if(color.type == "rgb"):
        # bleu
        if(color.rgb == 'FF0070C0'):
            return "fournie"
        
        # violet
        elif (color.rgb == 'FF7030A0'):
            return "variant"

    return None


excel_file_name = "matrice_croisee_IDU_COMP_toutes_les_UE_CTI.xlsx"
base_dir = Path(__file__).resolve().parent
path = base_dir / "Documents_competences" / "matrices_croisees" / excel_file_name
excel_workbook = load_workbook(path)

result = []

for sheet in excel_workbook.worksheets:

    ue_by_col_number = {}
    regular_expression_ue_code = re.compile(r"UE\d+")

    # Détection des colonnes UE (max_row car nom des UE devraient être vers le haut du excel donc ça évite de regarder le reste pour rien)
    for row in sheet.iter_rows(max_row=15):
        for cell in row:
            # Search renvoie un Match (true) si trouvé sinon un NULL (false)
            if isinstance(cell.value, str) and regular_expression_ue_code.search(cell.value):
                ue_by_col_number[cell.column] = cell.value

    # Parcours des lignes pour avoir liaisons UE avec CE et AC
    for row in sheet.iter_rows():

        code = None
        description = None
        # row est la liste des cellules, pour avoir num de la ligne on prend numero de ligne de la premiere cellule
        row_number = row[0].row

        for cell in row:
            if isinstance(cell.value, str):

                if cell.value.startswith("CE") or cell.value.startswith("AC"):
                    code = cell.value

                elif code and description is None:
                    description = cell.value

        # Si pas une ligne avec une composante essentielle ou apprentissage critique
        if not code or not description:
            continue

        infos = {
            "code": code,
            "nom": description,
            "UE_liees": {}
        }

        # col = clé (numero col) et ue = valeur (code UE + nom)
        for col, ue in ue_by_col_number.items():

            separated_ue_text = ue.split()
            ue_code = separated_ue_text[0]
            ue_name = separated_ue_text[1]

            cell = sheet.cell(row_number, col)

            if str(cell.value).lower() == "x":

                # Récupère le type de la liaison (fournie, ciblee ou variant) ou None si il n'y a pas de liaison
                type_liaison = get_liaison_type(cell)

                if type_liaison is not None:
                    infos["UE_liees"][ue_code] = {"nom" : ue_name, "type_liaison" : type_liaison}

        result.append(infos)

print(result)