const fetch = require("isomorphic-fetch");
const fs = require("fs");
const pRetry = require("p-retry");

const results = [];
const baseURL = "https://www.bundeshaushalt-info.de/rest/2017/soll";

const fetchRetry = url => pRetry(() => fetch(url), { retries: 5 });

const makeFetcher = (incomeOrExpense, planType) => {
  const makeRequest = id => {
    const suffix = id ? `${id}/` : "";
    return fetchRetry(`${baseURL}/${incomeOrExpense}/${planType}/${suffix}`)
      .then(r => {
        console.log(r.url);
        return r.json();
      })
      .then(json => {
        results.push(json.detail);
        const branchChildren = json.childs.filter(c => !c.titleDetail);
        return Promise.all(branchChildren.map(c => c.a).map(makeRequest));
      });
  };
  return makeRequest;
};

const getFunktionIncome = makeFetcher("einnahmen", "funktion");
const getFunktionExpenses = makeFetcher("ausgaben", "funktion");

Promise.all([getFunktionExpenses(), getFunktionIncome()]).then(() => {
  const json = JSON.stringify(results);
  fs.writeFile("functions.json", json, "utf8", () => console.log("Done! 🎉"));
});

const getGruppeIncome = makeFetcher("einnahmen", "gruppe");
const getGruppeExpenses = makeFetcher("ausgaben", "gruppe");

Promise.all([getGruppeExpenses(), getGruppeIncome()]).then(() => {
  const json = JSON.stringify(results);
  fs.writeFile("gruppen.json", json, "utf8", () => console.log("Done! 🎉"));
});
