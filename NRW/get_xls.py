import os
import requests


def maybe_make_data_dir():
    if not os.path.exists("./data"):
        os.makedirs("./data")


def main():
    url = "http://www.haushalt.fm.nrw.de/daten/hh2017.ges/daten/pdf/2017/Haushaltsplan_2017_Rohdaten.xls"
    r = requests.get(url)
    maybe_make_data_dir()
    with open("./data/Haushaltsplan_2017_Rohdaten.xls", 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    print("Downloaded! ✅")


if __name__ == "__main__":
    main()