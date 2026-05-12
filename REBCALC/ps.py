import csv
import json
from collections import defaultdict
from datetime import datetime

def csv_to_mongo_array(csv_file, json_file):
    labs_dict = defaultdict(lambda: {
        "partner": "",
        "region": "",
        "city": "",
        "institution": "",
        "address": "",
        "contractor": "",
        "phone": "",
        "edrpou": "",
        "manager": "",
        "districts": [],
        "devices": [],
        "tasks": []
    })

    # спробуємо кілька роздільників
    for delimiter in ['\t', ';', ',']:
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            if reader.fieldnames and "Edrpou" in [fn.strip().replace('\ufeff','') for fn in reader.fieldnames]:
                # нормалізуємо назви колонок
                reader.fieldnames = [fn.strip().replace('\ufeff','') for fn in reader.fieldnames]

                for row in reader:
                    row = {k.strip().replace('\ufeff',''): (v or "").strip() for k,v in row.items()}
                    edrpou = row.get("Edrpou", "")
                    if not edrpou:
                        continue

                    lab = labs_dict[edrpou]
                    lab["edrpou"] = edrpou
                    lab["partner"] = row.get("name", "")
                    lab["institution"] = row.get("name", "")
                    lab["region"] = row.get("region", "")
                    lab["city"] = row.get("sity", "")
                    lab["address"] = row.get("adress", "")
                    lab["manager"] = row.get("emploer", "")
                    if lab["manager"]:
                        lab["districts"] = [lab["manager"]]

                    product = row.get("product", "")
                    category = row.get("Category", "")
                    if product:
                        entry = {
                            "name": product,
                            "date": None,
                            "quantity": None
                        }
                        date_str = row.get("Date", "")
                        if date_str:
                            try:
                                entry["date"] = datetime.strptime(date_str, "%d.%m.%Y").isoformat()
                            except:
                                entry["date"] = date_str
                        qty = row.get("quantity", "")
                        if qty.isdigit():
                            entry["quantity"] = int(qty)
                        else:
                            entry["quantity"] = qty or None

                        if row.get("IS device", "").upper() == "YES":
                            device_entry = {
                                "category": category,
                                "name": product,
                                "rent": row.get("Rent", "").upper() == "YES",
                                "debt": row.get("Rent", "").upper() == "YES",
                                "date": entry["date"],
                                "quantity": entry["quantity"],
                                "reagents": []
                            }
                            lab["devices"].append(device_entry)
                        else:
                            matched = next((d for d in lab["devices"] if d["category"] == category), None)
                            if matched:
                                matched["reagents"].append(entry)
                            else:
                                lab["devices"].append({
                                    "category": category,
                                    "name": None,
                                    "rent": False,
                                    "debt": False,
                                    "date": None,
                                    "quantity": None,
                                    "reagents": [entry]
                                })
                break

    labs = list(labs_dict.values())
    with open(json_file, "w", encoding="utf-8") as out:
        json.dump(labs, out, ensure_ascii=False, indent=2)

    print(f"✅ Збережено {len(labs)} лабораторій у {json_file}")

# Виклик
csv_to_mongo_array("ЛАБИ.csv", "labs.json")
