import json


def main():
    with open("data.json") as infile:
        data = json.load(infile)
    structured = {
        "Einzelplan": {},
        "Kapitel": {},
        "Gruppe": {},
        "Funktion": {},
    }
    for entry in data:
        for key, value in entry.items():
            entry_type, number = key.split(" ")
            structured[entry_type][number] = value
    save(structured)


def save(data):
    with open("./structured.json", "w") as outfile:
        json.dump(data, outfile, indent=2)


if __name__ == "__main__":
    main()