import json

import requests
from scrapy import Selector
from xlrd import open_workbook
from requests_threads import AsyncSession


def get_numbers():
    with open('./data/Haushaltsplan_2017_Rohdaten.xls', 'rb') as infile:
        wb = open_workbook(file_contents=infile.read())
        examples = {}
        for s in wb.sheets():
            for row in range(1, s.nrows):
                # rows are Einzelplan,Kapitel,Gruppe,Zählnummer,Funktion
                einzelplan = int(s.cell(row, 0).value)
                kapitel = int(s.cell(row, 1).value)
                gruppe = int(s.cell(row, 2).value)
                zaehlnummer = int(s.cell(row, 3).value)
                funktion = int(s.cell(row, 4).value)
                key = '{}-{}-{}-{}'.format(einzelplan, kapitel, gruppe, funktion)
                examples[key] = {"einzelplan": einzelplan,
                                 "kapitel": kapitel,
                                 "gruppe": gruppe,
                                 "zaehlnummer": zaehlnummer,
                                 "funktion": funktion}
        return examples.values()


def get_cookiejar():
    resp = requests.get("http://www.haushalt.fm.nrw.de/grafik/index.php?year=2017&data_type=1&type=-1")
    return resp.cookies


def generate_urls(examples):
    for i, values in enumerate(examples):
        url = "http://www.haushalt.fm.nrw.de/grafik/ajax.php?id={einzelplan:02d}_{kapitel:03d}_{gruppe:03d}_{zaehlnummer:02d}_{funktion:03d}&detailView=1".format(
            **values
        )
        yield url
        # if i == 150:
        #     return


def extract_info(text):
    s = Selector(text=text)
    sections = s.css(".labels .section")
    details = {}
    for section in sections:
        number = section.css(".label ::text").extract_first()
        text = section.css("h4 ::text").extract_first()
        if not text:
            text = section.css("p ::text").extract_first()
        details[number] = text
    return details


session = AsyncSession(n=100)


async def _main():
    examples = get_numbers()
    cj = get_cookiejar()
    data = []
    for url in generate_urls(examples):
        response = await session.get(url, cookies=cj)
        details = extract_info(response.text)
        print(url, details)
        data.append(details)
    persist(data)


def persist(data):
    with open("./data.json", "w") as outfile:
        json.dump(data, outfile)


if __name__ == '__main__':
    session.run(_main)