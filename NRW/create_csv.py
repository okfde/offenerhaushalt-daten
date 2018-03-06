import csv

from xlrd import open_workbook


def main():
    data = xls_to_list()
    with open("./data/haushalt_nrw.csv", "w") as outfile:
        writer = csv.writer(outfile)
        for row in data:
            writer.writerow(row)


def xls_to_list():
    with open('./data/Haushaltsplan_2017_Rohdaten.xls', 'rb') as infile:
        wb = open_workbook(file_contents=infile.read())
        contents = []
        for sheet in wb.sheets():
            for a_row in sheet.get_rows():
                contents.append([a.value for a in a_row])
        return contents


if __name__ == "__main__":
    main()