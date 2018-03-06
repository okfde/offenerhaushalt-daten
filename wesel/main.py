import csv

def load_products():
    with open("./liste_produkte.csv", encoding="cp1252") as infile:
        reader = csv.reader(infile, delimiter=";")
        return {line[0]: line[1] for line in reader}


def load_haushalt():
    with open("./hhplan2017.csv", encoding="cp1252") as infile:
        reader = csv.DictReader(infile, delimiter=";")
        return list(reader)


def load_accounts():
    with open("./kontenrahmen.csv", encoding="cp1252") as infile:
        reader = csv.DictReader(infile, delimiter=";")
        return {line["Konto beginnend mit"]: line["E/A"] for line in reader}


def get_profitcenter_title(line, products):
    p_center = line["Profitcenter"]
    assert len(p_center) in [5, 6], (p_center, len(p_center), line)
    if len(p_center) == 6:
        first_level = p_center[:2]
        second_level = p_center[:4]
    else:
        first_level = p_center[:1]
        second_level = p_center[:3]
    return products[first_level], products[second_level]


def save_data(data):
    with open("./haushalt_enriched.csv", "w") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=data[0].keys())
        writer.writeheader()
        for line in data:
            writer.writerow(line)


def split_years(data):
    split = []
    for line in data:
        for ignore_key in ["VE 2018", "Plan 2021", "Plan 2022"]:
            line.pop(ignore_key)
        values = []
        for key in ["Ist 2015", "Ist 2016", "Plan 2016", "Plan 2017", "Plan 2018", "Plan 2019", "Plan 2020"]:
            value_type, year = key.split(" ")
            values.append({"year": year, "value_type": value_type, "value": line.pop(key)})
        for value in values:
            current_entry = line.copy()
            current_entry["Jahr"] = value["year"]
            current_entry["Plan/Ist"] = value["value_type"]
            current_entry["Betrag"] = value["value"]
            split.append(current_entry)
    return split


def add_budget_direction(data, account_data):
    collected = []
    for line in data:
        line["Art"] = account_data.get(line["Kostenart"][:3])
        if not line["Art"]:
            if line["Kostenart"][:2] in ["55", "69", "79", "72", "73", "74", "68", "97", "98"]:
                line["Art"] = "inv. Auszahlungen"  # This one is missing from the data but we think it is to be ignored
                continue
            line["Art"] = account_data[line["Kostenart"][:2]]
        if line["Art"] != "inv. Auszahlungen":
            collected.append(line)
    return collected


def main():
    haushalt = load_haushalt()
    products = load_products()
    for line in haushalt[:-1]:  # last line contains sums, skip it
        line["Profitcenter 1"], line["Profitcenter 2"] = get_profitcenter_title(line, products)
    account_data = load_accounts()
    with_direction = add_budget_direction(haushalt, account_data)
    split = split_years(with_direction)
    save_data(split)

if __name__ == '__main__':
    main()