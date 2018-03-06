import json

import requests
from scrapy import Selector

from read import get_cookiejar


def activate_saving_groups(cookie_jar):
    requests.get("http://www.haushalt.fm.nrw.de/grafik/index.php?category=1", cookies=cookie_jar)


def activate_income(cookie_jar):
    requests.get("http://www.haushalt.fm.nrw.de/grafik/index.php?type=1", cookies=cookie_jar)


def activate_expenses(cookie_jar):
    requests.get("http://www.haushalt.fm.nrw.de/grafik/index.php?type=2", cookies=cookie_jar)


def main():
    cj = get_cookiejar()
    activate_expenses(cj)
    activate_saving_groups(cj)
    expenses = get_page_for(None, cj)
    activate_income(cj)
    income = get_page_for(None, cj)

    combined = {**income, **expenses}
    save(combined)
    print("🎉  done!")


def save(data):
    with open("./data/einzelplaene.json", "w") as outfile:
        json.dump(data, outfile, indent=2)


def get_page_for(number, cj):
    url = "http://www.haushalt.fm.nrw.de/grafik/ajax.php"
    suffix = ""
    if number:
        suffix = "?selection={}".format("+".join(number.split()))
    response = requests.get(url+suffix, cookies=cj)
    s = Selector(text=response.text)
    results = {}
    if suffix == "?selection=03":
        print(response.text)
    for tr in s.css("tr:not(:first-child)"):
        id = tr.css("::attr(id)").extract_first()
        if id.startswith("03"):
            print(url + suffix)
            # print(id)
        name = tr.css(".col3 ::text").extract_first()
        results[id] = name
        if len(id) < len("n n"):
            results = {**results, **get_page_for(id, cj)}
    return results


if __name__ == '__main__':
    main()