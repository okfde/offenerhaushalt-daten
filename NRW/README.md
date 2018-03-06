# NRW Budget scraper and parser


## 🐍 Install
```bash
pipenv install
```

## 🏃Running
- Run `get_xls.py` to download the Excel-File containing the basic budget file (will be put in `./data/`)
- Run `create_csv.py` to convert the Excel file to csv
- Run `gruppen.py` to get a list of the names of all groups and sub-groups from the `Gruppen`-Ansicht
- Run `einzelplaene.py` to get a list of the names and chapters from the `Einzelpläne`-Ansict.
- Run `funktionen.py` to get a list of the names of all functions and sub-functions from the `Funktionen`-Ansicht
- Run `enrich_csv` to feed the group and function data back into the csv file (creates a new `./data/enriched.csv`) file to be imported to openbudgets


## 🤓 Reference
- http://www.haushalt.fm.nrw.de/grafik/index.php?category=1