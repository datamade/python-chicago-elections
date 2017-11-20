chi-elections
=============

chi-elections is a Python package for loading and parsing election results from the [Chicago Board of Elections](http://www.chicagoelections.com/).

Summary Results
---------------

The Board of Elections provides election-night results at a racewide level.  The file lives at

http://www.chicagoelections.com/results/ap/summary.txt

before election day, for testing.

It lives at

http://www.chicagoelections.com/ap/summary.txt

on election night.

### Text layout

From http://www.chicagoelections.com/results/ap/text_layout.txt:

Summary Export File Format      Length  Column Position
Contest Code                    4       1-4
Candidate Number                3       5-7
Num. Eligible Precincts         4       8-11
Votes                           7       12-18
Num. Completed precincts        4       19-22
Party Abbreviation              3       23-25
Political Subdivision Abbrev    7       26-32
Contest name                    56      33-88
Candidate Name                  38      89-126
Political subdivision name      25      127-151
Vote For                        3       152-154

### Gotchas

Prior to election night, the test file will include all fields.  At some point on election night, the file will only contain the numeric values in the first 22 columns.

This means that you need to:

* Make sure you save candidate names in some way, like a database, before election night
* Make sure you store ballot order (Candidate Number in the text layout above) with the candidate.  You'll need to use this, in combination with Contest Code, to look up the cached candidates.

At some point at the end of election night, the results file will no longer be available at http://www.chicagoelections.com/ap/summary.txt and will be available at http://www.chicagoelections.com/results/ap/summary.txt
.  However, it will not be updated. You'll need to scrape, enter or load results in some other way if you need updates after election night.


### Results client

To access the results:

    from chi_elections import SummaryClient

    client = SummaryClient()
    client.fetch()
    mayor = next(r for r in client.races if r.name == "Mayor")
    self.assertEqual(len(mayor.candidates), 5)

    rahm = next(c for c in mayor.candidates
                if c.full_name == "RAHM EMANUEL")
    print(rahm.vote_total)

If you want to specify an alternate url, for example the test URL, pass it to the constructor of `SummaryClient`:

    client = SummaryClient(url='http://www.chicagoelections.com/results/ap/summary.txt')


Precinct Results
----------------

After election night, precinct-level results are published to http://www.chicagoelections.com/en/election3.asp.  The results are HTML files, so we have to scrape the results from HTML tables.

### Results client

To access the results:

    from chi_elections import elections

    muni_elections = [election for name, election in
                      elections().items() if 'municipal' in name.lower()]

    for election in muni_elections:
        for name, race in election.races.items():
            if 'alderman' in name.lower() or 'mayor' in name.lower():
                for precinct, votes in race.precincts.items():
		    print(precinct, votes)

### Command Line Interface

To download a CSV version of the summary file, run:

    chi_elections summary > results.csv

To hit the test file:

    chi_elections summary --test > results.csv

