import csv
import json


def main():
    content = get_contents()
    funktionen = load_json("./data/funktionen.json")
    gruppen = load_json("./data/gruppen.json")
    ep_and_group = load_json("./data/einzelplaene.json")
    converted = []
    for row in content:
        with_function = add_funktionen(row, funktionen, "Funktion")
        with_group = add_funktionen(with_function, gruppen, "Gruppe")
        with_einzelplan = add_einzelplan(with_group, ep_and_group)
        with_type = add_type(with_einzelplan)
        converted.append(with_type)

    long_format = split(converted)
    persist(long_format)


def split(data):
    collected = []
    for row in data:
        collected.append(makerow(row, 2015, False, row["Ist 2015 in Euro"]))
        collected.append(makerow(row, 2016, True, row["Ansatz 2016 in Euro"]))
        collected.append(makerow(row, 2017, True, row["Ansatz 2017 in Euro"]))
    return collected


def add_type(row):
    is_income = float(row["Gruppe"]) < 400
    row["Einnahme"] = "Einnahmen" if is_income else "Ausgaben"
    return row


def makerow(row, year, is_plan, value):
    copy = row.copy()
    copy["year"] = year
    copy["plan"] = "Soll" if is_plan else "Ist"
    copy["value"] = value
    del copy["Ist 2015 in Euro"]
    del copy["Ansatz 2016 in Euro"]
    del copy["Ansatz 2017 in Euro"]
    return copy


def get_contents():
    with open("./data/haushalt_nrw.csv") as infile:
        reader = csv.DictReader(infile)
        return [row for row in reader]


def load_json(filename):
    with open(filename) as infile:
        return json.load(infile)


def add_einzelplan(row, data):
    ep = "{:02d}".format(int(float(row["Einzelplan"])))
    chapter = "{:03d}".format(int(float(row["Kapitel"])))
    row["Einzelplan_Name"] = data[ep]
    row["Kapitel_Name"] = data["{} {}".format(ep, chapter)]
    return row


def add_funktionen(row, funktionen, column_name):
    funktion = list(row[column_name].split(".")[0])
    if len(funktion) == 2:
        funktion = ["0"] + funktion
    for i in range(1, 4):
        key = " ".join(funktion[0:i])
        row["{} {}".format(column_name, i)] = funktionen[key]
    return row


def persist(data):
    with open("./data/enriched.csv", "w") as outfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(outfile, fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

if __name__ == "__main__":
    main()