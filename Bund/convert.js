const fs = require("fs");

const makeKeyedFile = filename => {
  const loadData = (err, data) => {
    const functionsMap = JSON.parse(
      data
    ).reduce((collectedData, currentEntry) => {
      collectedData[currentEntry.address] = currentEntry.label;
      return collectedData;
    }, {});
    fs.writeFile(
      `${filename}-keyed.json`,
      JSON.stringify(functionsMap, null, 2),
      "utf8",
      () => console.log("Done! 🎉")
    );
  };

  fs.readFile(`./${filename}.json`, "utf8", loadData);
};

makeKeyedFile("functions");
makeKeyedFile("gruppen");
