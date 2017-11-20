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
        self.index = index
        self.length = length
        self.transform = transform
        self.name = None

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
    # Summary Export File Format           Length    Column Position
    # Contest Code                         4         1-4
    # Candidate Number                     3         5-7
    # # of Eligible Precincts              4         8-11
    # Votes                                7         12-18
    # # Completed precincts                4         19-22
    # Party Abbreviation                   3         23-25
    # Political Subdivision Abbreviation   7         26-32
    # Contest name                         56        33-88
    # Candidate Name                       38        89-126
    # Political subdivision name           25        127-151
    # Vote For                             3         152-154
    contest_code = FixedWidthField(0, 4, transform=int)
    candidate_number = FixedWidthField(4, 3, transform=int)
    precincts_total = FixedWidthField(7, 4, transform=int)
    vote_total = FixedWidthField(11, 7, transform=int)
    precincts_reporting = FixedWidthField(18, 4, transform=int)
    party = FixedWidthField(22, 3)
    reporting_unit_name = FixedWidthField(25, 7)
    race_name = FixedWidthField(32, 56)
    candidate_name = FixedWidthField(88, 38, transform=replace_single_quotes)
    reporting_unit_name = FixedWidthField(126, 25)
    vote_for = FixedWidthField(151, 3, transform=int)


class Result(object):
    def __init__(self, candidate_number, full_name, party, race, vote_total,
            reporting_unit_name):
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
    def __init__(self, contest_code, name, precincts_total=0,
            precincts_reporting=0, vote_for=1):
        self.contest_code = contest_code
        self.name = name
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
                reporting_unit_name=parsed['reporting_unit_name'],
            )
            race.candidates.append(result)
    
    def get_or_create_race(self, attrs):
        try:
            race = self._race_lookup[attrs['contest_code']]
        except KeyError:
            race = Race(
                contest_code=attrs['contest_code'],
                name=attrs['race_name'],
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
