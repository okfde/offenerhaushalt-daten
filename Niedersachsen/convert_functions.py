# tabula-Funktionen-Niedersachsen.csv comes from manually creating  a subsection of the
# official haushalt that only contains the overview tables for all Funktionen (read: a smaller pdf)
# feeding this into tabular and selecting the first two columns on every page
import json
import re

pattern = re.compile("\d+ \w+")
lastMatched = False
results = {}
collected = []
currentEntry= ""
with open("./tabula-Funktionen-Niedersachsen.csv") as infile:
    for line in infile.readlines():
        line = line.strip().strip('"').strip("-")
        if line in ["Fkt.", "EinnahmenNr."] or line.endswith(" insgesamt"):
            continue
        if pattern.match(line):
            collected.append(currentEntry)
            currentEntry = line
            continue
        currentEntry += line

for line in collected:
    key = line.split(" ")[0]
    value = " ".join(line.split(" ")[1:])
    results[key] = value

# Note that this misses two lines : 18/19 Kultur und Religion
# and 11/12 Allgemeinbildende und berufliche Schulen
# right now this needs to be corrected by hand
with open("./niedersachsen-funktionen.json", "w") as outfile:
    json.dump(results, outfile, indent=2)