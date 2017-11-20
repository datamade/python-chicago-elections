import codecs
import sys

import csv

import click

from .constants import SUMMARY_URL, TEST_SUMMARY_URL
from .precincts import Election
from .summary import SummaryClient, SummaryParser

if sys.version_info < 3:
    # Wrap sys.stdout into a StreamWriter to allow writing unicode.
    # See https://wiki.python.org/moin/PrintFails
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

@click.group()
def main():
    pass

@click.command()
@click.option('-f', '--file', type=click.File())
@click.option('--test/--no-test', default=False)
def summary(file, test):
    if test:
        url = TEST_SUMMARY_URL
    else:
        url = SUMMARY_URL

    if file:
        parser = SummaryParser()
        parser.parse(file.read())
        races = parser.races
    else:
        client = SummaryClient(url=url)
        client.fetch()
        races = client.races

    fieldnames = [
       'contest_code',
       'race_name',
       'precincts_total',
       'precincts_reporting',
       'vote_for',
       'candidate_number',
       'full_name',
       'party',
       'vote_total',
    ]
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    for race in races:
        race_attrs = race.serialize()
        for candidate_result in race.candidates:
            row = dict(**race_attrs)
            row.update(candidate_result.serialize())
            writer.writerow(row)

main.add_command(summary)
