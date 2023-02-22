chi-elections
=============

[![Build Status](https://travis-ci.org/datamade/python-chicago-elections.svg?branch=master)](https://travis-ci.org/datamade/python-chicago-elections)

chi-elections is a Python package for loading and parsing election results from the [Chicago Board of Elections](https://www.chicagoelections.gov/).

Summary Results
---------------

The Board of Elections provides election-night results at a racewide level.  The file lives at

https://chicagoelections.gov/results/ap/

before election day, for testing.

It lives at

https://chicagoelections.gov/ap

on election night.

Per the Chicago Board of Elections, the results file will contain candidate and race names on election night and be kept updated until all votes are counted.

### Text layout

From https://chicagoelections.gov/results/ap/SummaryExportFormat.xls:

```
Summary Export File Format           Length    Column Position
Record type                          1         1
Global contest order                 5         2-6
Global choice order                  5         7-11
# Completed precincts                5         12-16
Votes                                7         17-23
Contest Total registration           7         24-30
Contest Total ballots cast           7         31-37
Contest Name                        70         38-107
Choice Name                         50         108-157
Choice Party Name                   50         158-207
Choice Party Abbreviation            3         208-210
District Type Name                  50         211-260
District Type Global Order           5         261-265
# of Eligible Precincts              5         266-270
Vote For                             2         271-272
```

### Results client

To access the results:

```python
from chi_elections import SummaryClient

client = SummaryClient()
client.fetch()
mayor = next(r for r in client.races if r.name == "Mayor")
self.assertEqual(len(mayor.candidates), 5)

rahm = next(c for c in mayor.candidates
            if c.full_name == "RAHM EMANUEL")
print(rahm.vote_total)
```

If you want to specify an alternate url, for example the test URL, pass it to the constructor of `SummaryClient`:

```python
client = SummaryClient(url='http://www.chicagoelections.com/results/ap/summary.txt')
```

Precinct Results
----------------

**N.b., The format of precinct results has changed and needs to be updated.**

After election night, precinct-level results are published to https://chicagoelections.com/en/election-results.html.  The results are HTML files, so we have to scrape the results from HTML tables.

### Results client

To access the results:

from chi_elections import elections

```python
muni_elections = [election for name, election in
                  elections().items() if 'municipal' in name.lower()]

for election in muni_elections:
    for name, race in election.races.items():
        if 'alderman' in name.lower() or 'mayor' in name.lower():
            for precinct, votes in race.precincts.items():
                print(precinct, votes)
```                

### Command Line Interface

To download a CSV version of the summary file, run:

    chi_elections summary > results.csv

To hit the test file:

    chi_elections summary --test > results.csv

