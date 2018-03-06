# 🇩🇪 Bundeshaushalt

Tool to scrape the German Budget.


## ⬇️Install
- Clone the repository and `cd` to it
- `yarn install` or `npm install`

## 🏃Running
- `node scrape.js` - will fetch `Funktionen` and `Gruppen` from the bundeshaushalt-info website (and write to `functions.json` and `gruppen.json`)
- `node convert.js` - will key `Funktionen` and `Grouppen` by their numerical identifier (and write to `functions-keyed.json` and `gruppen-keyed.json`)
- `node merge.js` will read the existing `hh_2017_utf8.csv` (from the Download-section of bundeshaushalt-info) and add the columns `Gruppe {1,2,3}`, `Funktion {1,2,3]` and year
- the last step creates a new file called `haushalt-enriched` which can be imported into openspending



