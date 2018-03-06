import csv
import json
import os


BASE_PATH = "C:/Users/Michael/Documents/GitHub/offenerhaushalt-pipeline/bremen"


def read_chapters():
    chapters = {}
    with open("./kapitel.csv") as infile:
        reader = csv.reader(infile)
        for line in reader:
            chapters[line[0]] = line[1]
    return chapters


def add_chapters(line):
    # These were extracted by hand from the PDFs from the website
    einzelplan = {
        "00": "Bürgerschaft, Senat, Rechnungshof, Staatsgerichtshof, Bundesangelegenheiten, Datenschutz, Inneres, Frauen (L)",
        "01": "Justiz und Verfassung (L)",
        "02": "Kinder und Bildung, Kultur und Wissenschaft (L)",
        "03": "Arbeit (L)",
        "04": "Jugend, Soziales, Integration (L)",
        "05": "Gesundheit (L)",
        "06": "Umwelt, Bau und Verkehr (L)",
        "07": "Wirtschaft (L)",
        "08": "Häfen (L)",
        "09": "Finanzen (L)",
        "30": "Bürgerschaft, Senat, Inneres (S)",
        "31": "Sport (S)",
        "32": "Kinder und Bildung, Kultur (S)",
        "33": "Arbeit (S)",
        "34": "Jugend, Soziales (S)",
        "35": "Gesundheit (S)",
        "36": "Umwelt, Bau und Verkehr (S)",
        "37": "Wirtschaft (S)",
        "38": "Häfen (S)",
        "39": "Finanzen (S)"
    }
    kapitel = read_chapters()
    line["Einzelplan_Name"] = einzelplan[line["Hst."][:2]]
    line["Kapitel_Name"] = kapitel.get(line["Hst."][:4], "[keine Angabe ({})]".format(line["Hst."][:4]))

    return line


def save_as_json(data, name):
    with open(os.path.join(BASE_PATH, "bremen-{}.json".format(name)), "w") as outfile:
        json.dump(data, outfile, indent=2, ensure_ascii=False)


def jsonify_csv(name):
    collected = {}
    had_dash = False
    current_number = 0
    with open(os.path.join(BASE_PATH, "tabula-Bremen-{}.csv".format(name))) as infile:
        reader = csv.reader(infile)
        for line in reader:
            if line[0] != "":
                current_number = line[0]
                title = line[1]
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
    save_as_json(collected, name)


def get_json(name):
    with open(os.path.join(BASE_PATH, "bremen-{}.json".format(name))) as infile:
        return json.load(infile)


def save_data(data):
    with open(os.path.join(BASE_PATH, "haushalt-bremen-enriched.csv"), "w", newline="\n") as outfile:
        headers = data[0].keys()
        writer = csv.DictWriter(outfile, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def split_years(data):
    new_haushalt = []
    for line in data:
        value_2016 = line.pop("Anschlag 2016")
        value_2017 = line.pop("Anschlag 2017")

        line_2016 = line.copy()
        line_2017 = line.copy()
        line_2016["year"] = "2016"
        line_2017["year"] = "2017"
        line_2016["Betrag"] = value_2016
        line_2017["Betrag"] = value_2017
        new_haushalt.append(line_2016)
        new_haushalt.append(line_2017)
    return new_haushalt


def enrich_haushalt():
    with open(os.path.join(BASE_PATH, "Haushaltsdaten_2016-2017.csv")) as infile:
        reader = list(csv.DictReader(infile))
        groups = get_json("gruppen")
        functions = get_json("funktionen")
        for line in reader:
            gruppe = line['Hst.'][5:8]
            funktion = line['FKZ'].zfill(3)
            line["Gruppe 3"] = groups.get(gruppe, "N/A")
            line["Gruppe 2"] = groups[gruppe[:2] + "*"]
            line["Gruppe 1"] = groups[gruppe[:1] + "**"]
            line["Funktion 3"] = functions[funktion]
            line["Funktion 2"] = functions[funktion[:2] + "*"]
            line["Funktion 1"] = functions[funktion[:1] + "**"]
            line["Art"] = "Einnahmen" if line["Aggregat"].startswith("EINN") else "Ausgaben"
            add_chapters(line)
        split = split_years(reader)
        save_data(split)


def main():
    jsonify_csv("gruppen")
    jsonify_csv("funktionen")
    enrich_haushalt()


if __name__ == '__main__':
    main()
