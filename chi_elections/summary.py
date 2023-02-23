"""
Parse fixed-width summary file.

This file lives at

http://www.chicagoelections.com/results/ap/

before election day, for testing.

It lives at

www.chicagoelections.com/ap/

on election night.

This file provides racewide results.

"""
from collections import OrderedDict

import requests

from .constants import SUMMARY_URL
from .transforms import replace_single_quotes


class FixedWidthField(object):
    def __init__(self, index, length, transform=None):
        self.index = self._index(index)
        self.length = length
        self.transform = transform
        self.name = None

    def _index(self, index):
        return index

    def parse(self, s):

        val = s[self.index:self.index + self.length]
        val = val.strip()
        if self.transform is None:
            return val
        else:
            try:
                return self.transform(val)
            except ValueError:
                return None


class OneIndexedFixedWidthField(FixedWidthField):

    def _index(self, index):
        return index - 1


class FixedWidthParserMeta(type):
    def __new__(cls, name, parents, dct):
        dct['_fields'] = []
        for k, v in list(dct.items()):
            if isinstance(v, FixedWidthField):
                v.name = k
                dct['_fields'].append(v)
                del dct[k]

        new_cls = super(FixedWidthParserMeta, cls).__new__(cls, name, parents, dct)
        return new_cls


class FixedWidthParser(object, metaclass=FixedWidthParserMeta):

    def parse_line(self, line):
        attrs = {}
        for field in self._fields:
            attrs[field.name] = field.parse(line)

        return attrs 


class ResultParser(FixedWidthParser):
    """
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

    Source: https://chicagoelections.gov/results/ap/SummaryExportFormat.xls
    """
    record_type = OneIndexedFixedWidthField(1, 1, transform=int)
    contest_code = OneIndexedFixedWidthField(2, 5, transform=int)
    candidate_number = OneIndexedFixedWidthField(7, 5, transform=int)
    precincts_reporting = OneIndexedFixedWidthField(12, 5, transform=int)
    vote_total = OneIndexedFixedWidthField(17, 7, transform=int)
    race_total_registration = OneIndexedFixedWidthField(24, 7, transform=int)
    race_total_ballots_cast = OneIndexedFixedWidthField(31, 7, transform=int)
    race_name = OneIndexedFixedWidthField(38, 70)
    candidate_name = OneIndexedFixedWidthField(108, 50, transform=replace_single_quotes)
    party = OneIndexedFixedWidthField(158, 50)
    party_abbreviation = OneIndexedFixedWidthField(208, 3)
    reporting_unit_name = OneIndexedFixedWidthField(211, 50)
    reporting_unit_code = OneIndexedFixedWidthField(261, 5, transform=int)
    precincts_total = OneIndexedFixedWidthField(266, 5, transform=int)
    vote_for = OneIndexedFixedWidthField(271, 2, transform=int)


class Result(object):
    def __init__(self, candidate_number, full_name, party, race, vote_total):
        self.candidate_number = candidate_number
        self.full_name = full_name
        self.party = party
        self.race = race
        self.vote_total = vote_total

    def __str__(self):
        return "{}: {}d".format(self.name, self.vote_total)

    def serialize(self):
        return OrderedDict((
            ('candidate_number', self.candidate_number),
            ('full_name', self.full_name),
            ('party', self.party),
            ('vote_total',self.vote_total),
        ))


class Race(object):
    def __init__(self, contest_code, name, reporting_unit_name, total_ballots_cast,
            precincts_total=0, precincts_reporting=0, vote_for=1):
        self.contest_code = contest_code
        self.name = name
        self.reporting_unit_name = reporting_unit_name
        self.total_ballots_cast = total_ballots_cast
        self.candidates = []
        self.precincts_total = precincts_total
        self.precincts_reporting = precincts_reporting
        self.vote_for = vote_for

    def serialize(self):
        return OrderedDict((
            ('contest_code', self.contest_code),
            ('race_name', self.name),
            ('precincts_total', self.precincts_total),
            ('precincts_reporting', self.precincts_reporting),
            ('vote_for', self.vote_for),
        ))

    def __str__(self):
        return self.name


class SummaryParser(object):
    def __init__(self):
        self._result_parser = ResultParser()

    def parse(self, s):
        self.races = []
        self._race_lookup = {}

        for line in s.splitlines(True):
            parsed = self._result_parser.parse_line(line)
            race = self.get_or_create_race(parsed)
            result = Result(
                candidate_number=parsed['candidate_number'],    
                vote_total=parsed['vote_total'],
                party=parsed['party'],
                race=race,
                full_name=parsed['candidate_name'],
            )
            race.candidates.append(result)
    
    def get_or_create_race(self, attrs):
        try:
            race = self._race_lookup[attrs['contest_code']]
        except KeyError:
            race = Race(
                contest_code=attrs['contest_code'],
                name=attrs['race_name'],
                reporting_unit_name=attrs['reporting_unit_name'],
                total_ballots_cast=attrs['race_total_ballots_cast'],
                precincts_total=attrs['precincts_total'],
                precincts_reporting=attrs['precincts_reporting'],
                vote_for=attrs['vote_for'],
            )
            self._race_lookup[attrs['contest_code']] = race
            self.races.append(race)
        
        return race


class SummaryClient(object):
    DEFAULT_URL = SUMMARY_URL 

    def __init__(self, url=None):
        if url is None:
            url = self.DEFAULT_URL
        self._url = url

        self._parser = SummaryParser()

    def get_url(self):
        return self._url

    def fetch(self):
        url = self.get_url()
        r = requests.get(url)
        self._parser.parse(r.text)

    @property
    def races(self):
        return self._parser.races
