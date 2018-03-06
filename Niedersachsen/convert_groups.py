import json
import re


def strip_all(text):
    return text.strip().strip('"').strip("-")

pattern = re.compile("\d+ [\w+\"]")
lastMatched = False
results = {}
collected = []
currentEntry = ""
with open("./tabula-Gruppen-Niedersachsen.csv") as infile:
    for line in infile.readlines():
        line = strip_all(line)
        if line in ["Grp.", "EinnahmenNr.", "1 2"] or line.endswith(" insgesamt"):
            continue
        if pattern.match(line):
            collected.append(currentEntry)
            currentEntry = line
            continue
        currentEntry += line

repetition_pattern = re.compile("\(\d+ - \d+\)$")

for line in collected:
    key = line.split(" ")[0]
    value = strip_all(" ".join(line.split(" ")[1:]))
    rep_matches = repetition_pattern.search(value)
    # sometimes a line ends with a range to which this row applies
    # so the line might looks something like this:
    # 731 expenses for bikes (731-745)
    # here we expand those lines into multiple entries
    if rep_matches:
        match = rep_matches.group(0)
        start, end = int(match[1:4]), int(match[6:10])
        for sub_key in range(start, end + 1):
            results[str(sub_key)] = value
    results[key] = value

with open("./niedersachsen-gruppen.json", "w") as outfile:
    json.dump(results, outfile, indent=2)
