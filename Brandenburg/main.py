import csv
import json
import os
from collections import defaultdict


def read_chapters():
    chapters = {}
    with open("./kapitel.csv") as infile:
        reader = csv.reader(infile, delimiter=";")
        for line in reader:
            chapters[line[0]] = line[1]
    return chapters


def add_chapters(line):
    # These were extracted by hand from the website
    einzelplan = {
        "01": "Landtag",
        "02": "Ministerpräsidentin, Ministerpräsident und Staatskanzlei",
        "03": "Ministerium des Innern und für Kommunales",
        "04": "Ministerium der Justiz und für Europa und Verbraucherschutz",
        "05": "Ministerium für Bildung, Jugend und Sport",
        "06": "Ministerium für Wissenschaft, Forschung und Kultur",
        "07": "Ministerium für Arbeit, Soziales, Gesundheit, Frauen und Familie",
        "08": "Ministerium für Wirtschaft und Energie",
        "10": "Ministerium für Ländliche Entwicklung, Umwelt und Landwirtschaft",
        "11": "Ministerium für Infrastruktur und Landesplanung",
        "12": "Ministerium der Finanzen",
        "13": "Landesrechnungshof",
        "14": "Verfassungsgericht des Landes Brandenburg",
        "20": "Allgemeine Finanzverwaltung",
    }
    kapitel = read_chapters()
    line["Einzelplan_Name"] = einzelplan[line["Kapitel"][:2]]
    line["Kapitel_Name"] = kapitel[line["Kapitel"][:5]]

    return line


def join_and_undash(parts):
    result = ""
    for i in range(len(parts)):
        prev = parts[i - 1] if i > 0 else ""
        current_part = parts[i]
        if current_part.endswith("-"):
            current_part = current_part[:-1]
        if prev.endswith("-"):
            result += current_part
        else:
            result += " " + current_part
    return result.strip()


def jsonify_csv(reader):
    collected = defaultdict(list)
    current_number = "0"
    for line in reader:
        current_number = line[0] or current_number
        collected[current_number].append(line[1])
    for entry in collected.keys():
        collected[entry] = join_and_undash(collected[entry])

    return collected


def read_data(data_type):
    with open(os.path.join("tabula-{}-brandenburg.csv".format(data_type))) as infile:
        reader = csv.reader(infile)
        return list(reader)


def read_haushalt():
    with open("./haushalt-brandenburg.csv") as infile:
        data = csv.DictReader(infile, delimiter=",");
        return list(data)


def split_years(haushalt):
    new_haushalt = []
    for line in haushalt:
        value_2016 = line.pop("Ansatz 2016 in EUR")
        value_2017 = line.pop("Ansatz 2017 in EUR")
        value_2018 = line.pop("Ansatz 2018 in EUR")
        line_2016 = line.copy()
        line_2017 = line.copy()
        line_2018 = line.copy()
        line_2016["Jahr"] = "2016"
        line_2017["Jahr"] = "2017"
        line_2018["Jahr"] = "2018"
        line_2016["Ansatz"] = value_2016
        line_2017["Ansatz"] = value_2017
        line_2018["Ansatz"] = value_2018

        new_haushalt.append(line_2016)
        new_haushalt.append(line_2017)
        new_haushalt.append(line_2018)
    return new_haushalt


def main():
    groups = read_data('gruppen')
    groups_keyed = jsonify_csv(groups)
    functions = read_data('funktionen')
    functions_keyed = jsonify_csv(functions)
    haushalt = read_haushalt()
    enriched = enrich(haushalt, functions_keyed, groups_keyed)
    split = split_years(enriched)
    write_haushalt(split)


def write_haushalt(haushalt):
    with open("./haushalt-brandenburg-enriched.csv", "w") as outfile:
        fieldnames = haushalt[0].keys()
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in haushalt:
            writer.writerow(row)


def enrich(haushalt, functions, groups):
    for line in haushalt:
        gruppe = line["Titel"]
        funktion = line["FZ"]
        line["Gruppe 3"] = groups.get(gruppe[:3])
        line["Gruppe 2"] = groups.get(gruppe[:2], "N/A")
        line["Gruppe 1"] = groups[gruppe[:1]]
        line["Funktion 3"] = functions.get(funktion)
        line["Funktion 2"] = functions[funktion[:2]]
        line["Funktion 1"] = functions[funktion[:1]]
        line = add_chapters(line)
        line['Art'] = "Einnahme" if line["Kapitel"][:2] in ["00", "01", "02", "03"] else "Ausgabe"

    return haushalt

if __name__ == '__main__':
    main()
