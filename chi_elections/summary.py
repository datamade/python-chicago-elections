"""
Parse fixed-width summary file.

This file lives at

http://www.chicagoelections.gov/results/ap/

before election day, for testing.

It lives at

www.chicagoelections.gov/ap/

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

        val = s[self.index : self.index + self.length]
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
        dct["_fields"] = []
        for k, v in list(dct.items()):
            if isinstance(v, FixedWidthField):
                v.name = k
                dct["_fields"].append(v)
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
    completed_precincts = FixedWidthField(11, 5, transform=int)
    votes = FixedWidthField(16, 7, transform=int)
    total_registration = FixedWidthField(23, 7, transform=int)
    total_ballots_cast = FixedWidthField(30, 7, transform=int)
    race_name = FixedWidthField(37, 70)
    choice_name = FixedWidthField(107, 50, transform=replace_single_quotes)
    party = FixedWidthField(157, 40)
    party_abbrev = FixedWidthField(207, 3)
    district_type = FixedWidthField(210, 50)
    eligible_precincts = FixedWidthField(265, 5, transform=int)
    vote_for = FixedWidthField(271, 2, transform=int)


class Result(object):
    def __init__(
        self,
        choice_name,
        party,
        race,
        votes,
    ):
        self.choice_name = choice_name
        self.party = party
        self.race = race
        self.votes = votes

    def __str__(self):
        return "{}: {}d".format(self.choice_name, self.votes)

    def serialize(self):
        return OrderedDict(
            (
                # ("candidate_number", self.candidate_number),
                ("choice_name", self.choice_name),
                ("party", self.party),
                ("votes", self.votes),
            )
        )


class Race(object):
    def __init__(
        self,
        name,
        eligible_precincts=0,
        completed_precincts=0,
        total_registration=0,
        total_ballots_cast=0,
        vote_for=1,
    ):
        self.name = name
        self.candidates = []
        self.eligible_precincts = eligible_precincts
        self.completed_precincts = completed_precincts
        self.total_registration = total_registration
        self.total_ballots_cast = total_registration
        self.vote_for = vote_for

    def serialize(self):
        return OrderedDict(
            (
                ("race_name", self.name),
                ("total_registration", self.total_registration),
                ("total_ballots_cast", self.total_ballots_cast),
                ("eligible_precincts", self.eligible_precincts),
                ("completed_precincts", self.completed_precincts),
                ("vote_for", self.vote_for),
            )
        )

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
                votes=parsed["votes"],
                party=parsed["party"],
                race=race,
                choice_name=parsed["choice_name"],
            )
            race.candidates.append(result)

    def get_or_create_race(self, attrs):
        try:
            race = self._race_lookup[attrs["race_name"]]
        except KeyError:
            race = Race(
                eligible_precincts=attrs["eligible_precincts"],
                name=attrs["race_name"],
                completed_precincts=attrs["completed_precincts"],
                total_ballots_cast=attrs["total_ballots_cast"],
                vote_for=attrs["vote_for"],
            )
            self._race_lookup[attrs["race_name"]] = race
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
