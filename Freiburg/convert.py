from csv import DictReader, DictWriter

FILENAME = "./freiburg_neu.csv"


def read_data():
    with open(FILENAME, encoding='cp1252') as infile:
        reader = DictReader(infile, delimiter=';')
        return list(reader)


def split(data):
    keys = []
    for year in ["Ergebnis 2015"] + ["Ansatz {}".format(year) for year in range(2016, 2019)]:
        for payment_type in ["Erträge", "Aufwendungen"]:
            keys.append({"key": "{} ({})".format(year, payment_type),
                         "year": year[-4:],
                         "type": payment_type})

    remove_keys = ["Ansatz {}(Saldo/Zuschussbedarf/Erträge - Aufwendungen)".format(year) for year in ["", "2016 ", "2018 "]]
    remove_keys.append("Ergebnis 2015 (Saldo/Zuschussbedarf/Erträge - Aufwendungen)")

    results = []
    for line in data:
        split = []
        for key in keys:
            split.append(dict(value=line.pop(key["key"]), type=key["type"], year=key["year"]))
        for key in remove_keys:
            line.pop(key)
        for entry in split:
            row = line.copy()
            row["Jahr"] = entry["year"]
            row["Art"] = entry["type"]
            row["Betrag"] = entry["value"]
            results.append(row)
    return results


def write_data(data):
    with open("./haushalt-freiburg-enriched.csv", "w", newline = '') as outfile:
        writer = DictWriter(outfile, fieldnames=data[0].keys())
        writer.writeheader()
        for line in data:
            writer.writerow(line)


def main():
    data = read_data()
    split_by_year = split(data)
    write_data(split_by_year)


if __name__ == '__main__':
    main()
