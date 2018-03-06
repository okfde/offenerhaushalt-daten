import csv
import json
import os


def read_chapters():
    chapters = {}
    with open("./kapitel.csv") as infile:
        reader = csv.reader(infile)
        for line in reader:
            chapters[line[0]] = line[1]
    return chapters


def add_chapters(line):
    # These were extracted by hand from the website
    einzelplan = {
        "01": "Landtag",
        "02": "Landesrechnungshof",
        "03": "Ministerpräsident, Staatskanzlei",
        "04": "Ministerium für Inneres und Bundesangelegenheiten",
        "05": "Finanzministerium",
        "06": "Ministerium für Wirtschaft, Arbeit, Verkehr und Technologie",
        "07": "Ministerium für Schule und Berufsbildung",
        "09": "Ministerium für Justiz, Kultur und Europa",
        "10": "Ministerium für Soziales, Gesundheit, Wissenschaft und Gleichstellung",
        "11": "Allgemeine Finanzverwaltung",
        "12": "Hochbaumaßnahmen und Raumbedarfsdeckung des Landes",
        "13": "Ministerum für Energiewende, Landwirtschaft, Umwelt und ländliche Räume",
        "14": "Informations- und Kommunikationstechnologien, E-Government und Organisation",
        "15": "Landesverfassungsgericht",
        "16": "InfrastrukturModernisierungsProgramm für unser Land Schleswig-Holstein (Impuls 2030)",
    }
    kapitel = read_chapters()
    line["Einzelplan_Name"] = einzelplan[line["Kapitel"][:2]]
    line["Kapitel_Name"] = kapitel.get(line["Kapitel"][:4], "[keine Angabe]")

    return line


def jsonify_csv(reader):
    collected = {}
    had_dash = False
    current_number = 0
    for line in reader:
        if line[0] != "":
            current_number = line[0]
            title = line[1].strip()
            if title.endswith("-"):
                had_dash = True
                title = title[:-1]
            else:
                had_dash = False
            collected[current_number] = title
            continue

        if had_dash:
            collected[current_number] += line[1]
        else:
            collected[current_number] += " " + line[1]
    return collected


def read_data(data_type):
    with open(os.path.join("tabula-{}.csv".format(data_type))) as infile:
        reader = csv.reader(infile)
        return list(reader)


def read_haushalt():
    with open("./hh17_csv.csv", encoding="cp1252") as infile:
        data = csv.DictReader(infile, delimiter=";")
        return list(data)


def split_years(haushalt):
    new_haushalt = []
    for line in haushalt:
        value_2015 = line.pop("Ist 2015 in T€")
        value_2016 = line.pop("Soll 2016 in T€")
        value_2017 = line.pop("Ansatz 2017 in T€")
        line_2015 = line.copy()
        line_2016 = line.copy()
        line_2017 = line.copy()
        line_2015["Jahr"] = "2015"
        line_2016["Jahr"] = "2016"
        line_2017["Jahr"] = "2017"
        line_2015["Wert"] = value_2015
        line_2016["Wert"] = value_2016
        line_2017["Wert"] = value_2017

        new_haushalt.append(line_2015)
        new_haushalt.append(line_2016)
        new_haushalt.append(line_2017)
    return new_haushalt


def extend_groups(groups):
    new_dict = {}
    for (key, value) in groups.items():
        if "-" in key:
            start, end = key.split("-")
            for i in padded_range(start, end):
                new_dict[i] = value
        if "/" in key:
            start, end = key.split("/")
            new_dict[start] = value
            new_dict[end] = value
        else:
            new_dict[key] = value
    return new_dict


def padded_range(start: str, end: str):
    assert len(start) == len(end), "start and end should have the same length: {} {}".format(start, end)
    length = len(start)
    for i in range(int(start), int(end) + 1):
        yield str(i).zfill(length)


def add_income_expense(data):
    for line in data:
        line['Art'] = "Einnahme" if line["Titel"][0] in ["0", "1", "2", "3"] else "Ausgabe"
    return data


def main():
    groups = read_data('gruppen')
    groups_keyed = extend_groups(jsonify_csv(groups))
    functions = read_data('funktionen')
    functions_keyed = extend_groups(jsonify_csv(functions))
    haushalt = read_haushalt()
    enriched = enrich(haushalt, functions_keyed, groups_keyed)
    split = split_years(enriched)
    with_direction = add_income_expense(split)
    write_haushalt(with_direction)


def write_haushalt(haushalt):
    with open("./haushalt-schleswig-holstein-enriched.csv", "w") as outfile:
        fieldnames = haushalt[0].keys()
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in haushalt:
            writer.writerow(row)


def enrich(haushalt, functions, groups):
    for line in haushalt:
        gruppe = line["Titel"]
        funktion = line["FKZ"]
        line["Gruppe 3"] = groups.get(gruppe[:3])
        line["Gruppe 2"] = groups.get(gruppe[:2], "N/A")
        line["Gruppe 1"] = groups[gruppe[:1]]
        line["Funktion 3"] = functions.get(funktion)
        line["Funktion 2"] = functions[funktion[:2]]
        line["Funktion 1"] = functions[funktion[:1]]
        line = add_chapters(line)
    return haushalt

if __name__ == '__main__':
    main()
