import json

def analyse_heures(data):
    resultats = {}

    for ue_id, ue in data.items():
        total_CM = 0
        total_TD = 0
        total_TP = 0

        modules = ue.get("modules", [])

        for module in modules:
            total_CM += module.get("CM", 0)
            total_TD += module.get("TD", 0)
            total_TP += module.get("TP", 0)

        total = total_CM + total_TD + total_TP

        if total > 0:
            pct_CM = round((total_CM / total) * 100, 1)
            pct_TD = round((total_TD / total) * 100, 1)
            pct_TP = round((total_TP / total) * 100, 1)
        else:
            pct_CM = pct_TD = pct_TP = 0

        resultats[ue_id] = {
            "nom": ue.get("nom", "Nom inconnu"),
            "total": total,
            "CM": total_CM,
            "TD": total_TD,
            "TP": total_TP,
            "%CM": pct_CM,
            "%TD": pct_TD,
            "%TP": pct_TP
        }

    return resultats


def afficher(resultats):
    sorted_ues = sorted(resultats.items(), key=lambda x: x[1]["total"], reverse=True)

    print("\n ANALYSE DES UE\n")

    for ue_id, d in sorted_ues:
        print(f"{ue_id} - {d['nom']}")
        print(f"  Total : {d['total']}h")
        print(f"  CM : {d['CM']}h ({d['%CM']}%)")
        print(f"  TD : {d['TD']}h ({d['%TD']}%)")
        print(f"  TP : {d['TP']}h ({d['%TP']}%)")
        print("-" * 40)

    total_global = sum(d["total"] for d in resultats.values())
    print(f"\n Total formation : {total_global}h")


# EXECUTION
with open("struct.json", "r", encoding="utf-8") as f:
    data = json.load(f)

res = analyse_heures(data)
afficher(res)