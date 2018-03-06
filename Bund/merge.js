const fs = require("fs");
const csv = require("csv");
const stringify = require("csv-stringify");
const _ = require("lodash");

const util = require("util");

const readFile = util.promisify(fs.readFile);

const enrichData = (data, groups, functions) => {
  const converted = data.map(row => {
    const singleFunctions = [...makeSubFunctions(row.funktion)];
    singleFunctions.forEach((number, index) => {
      row[`Funktion ${index + 1}`] = functions[number];
    });
    const singleGroups = [...makeSubGroups(row.titel)];
    singleGroups.forEach((number, index) => {
      row[`Gruppe ${index + 1}`] = groups[number];
    });
    return { ...row, date: 2017 };
  });
  writeFile(converted);
};

function* makeSubFunctions(number) {
  const padded = _.padStart(number, 3, "0");
  for (let i = 1; i <= 3; i++) {
    yield padded.slice(0, i);
  }
}

function* makeSubGroups(title) {
  const padded = _.padStart(title, 5, "0");
  for (let i = 1; i <= 3; i++) {
    yield padded.slice(0, i);
  }
}

const writeFile = data => {
  stringify(data, { header: true }, (err, csvText) => {
    fs.writeFile("haushalt-enriched.csv", csvText, "utf8", () =>
      console.log("Done! 🎉")
    );
  });
};

function getJSON(filename) {
  return readFile(filename, "utf-8").then(data => JSON.parse(data));
}

function main() {
  const functionsPromise = getJSON("./functions-keyed.json");
  const groupsPromise = getJSON("./gruppen-keyed.json");
  const csvPromise = readFile("./hh_2017_utf8.csv", "utf8");
  Promise.all([
    functionsPromise,
    groupsPromise,
    csvPromise
  ]).then(([functions, groups, csvFile]) => {
    csv.parse(csvFile, { columns: true, delimiter: ";" }, (err, data) => {
      enrichData(data, groups, functions);
    });
  });
}

main();
