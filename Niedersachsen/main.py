import csv
import re
import json

import math

pattern = re.compile("\d{4} \w+")


def get_json(filename):
    with open(filename) as infile:
        return json.load(infile)


def count_down(number):
    number = int(number)
    limit = math.floor(number / 10) * 10
    while number > limit:
        yield number
        number -= 1
    yield number
    yield math.floor(number / 10)


pattern = re.compile('(?P<chapter>\d{4})-(?P<group>\d{3}) (?P<foo>\d{2})')


def get_second_group(number, gruppen):
    for i in count_down(number):
        result = gruppen.get(str(i))
        if result:
            return result


def split_years(data):
    split = []
    for line in data:
        value_2017 = line.pop("Ansatz für 2017  (EUR)")
        value_2018 = line.pop("Ansatz für 2018  (EUR)")

        entry_2017 = line.copy()
        entry_2018 = line.copy()

        entry_2017["year"] = 2017
        entry_2018["year"] = 2018

        entry_2017["value"] = value_2017
        entry_2018["value"] = value_2018

        split.append(entry_2017)
        split.append(entry_2018)
    return split


def save_enriched_csv(data):
    with open("./haushalt-niedersachsen-enriched.csv", "w") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=data[0].keys())
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def main():
    with open("./haushalt-niedersachsen.csv") as infile:
        reader = csv.DictReader(infile, delimiter=";")
        gruppen = get_json("./niedersachsen-gruppen.json")
        funktionen = get_json("./niedersachsen-funktionen.json")
        collected = []
        for line in reader:
            parts = pattern.search(line["Haushaltsstelle"])
            group = parts.group("group")
            funktion = line["Funktion"].zfill(3)
            line["Gruppe 1"] = gruppen.get(group[0])
            line["Gruppe 2"] = get_second_group(group[0:2], gruppen)
            line["Gruppe 3"] = gruppen.get(group)
            line["Funktion 1"] = funktionen[funktion[:1]]
            line["Funktion 2"] = funktionen[funktion[:2]]
            line["Funktion 3"] = funktionen[funktion[:3]]
            line["E/A"] = "Einnahme" if line["E/A"] == "E" else "Ausgabe"
            collected.append(line)

    by_year = split_years(collected)
    save_enriched_csv(by_year)



if __name__ == '__main__':
    main()
