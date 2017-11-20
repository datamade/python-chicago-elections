"""
Parse tabular precinct-level results.
"""
import functools
import collections

import lxml.html
import requests

class Election(object):
    ELECTION_URL = 'https://chicagoelections.com/en/election-results.asp'
    
    def __init__(self, elec_code, name, session):
        self.elec_code = elec_code
        self.name = name
        self.url = self.ELECTION_URL
        self.session = session
        self._turnout = None

    @property
    def turnout(self):
        if not self._turnout:
            self.races
        return self._turnout

    @property
    @functools.lru_cache(maxsize=1)
    def races(self):
        response = self.session.get(self.url,
                                    params={'election': self.elec_code})
        page = lxml.html.fromstring(response.text)
        option_els = page.xpath(
            "//select[@name='race']/option")

        races = {}

        for option_el in option_els:
            name = option_el.text
            race_num = option_el.get('value')
            if 'registered voters' in name.lower():
                self._turnout = Race(self.elec_code,
                                     name, race_num, self.session)
            else:
                races[option_el.text] = Race(self.elec_code,
                                             name,
                                             race_num, self.session)

        return races
    
class Race(object):
    RESULTS_URL = 'https://chicagoelections.com/en/data-export.asp'
    
    def __init__(self, elec_code, name=None, number=None, session=None):
        self.elec_code = elec_code
        self.number = number
        self.name = name
        self.session = session

    def __str__(self):
        if self.name and self.number:
            return "{} ({})".format(self.name, self.number)
        elif self.name:
            return self.name
        elif self.number:
            return self.number
        else:
            return ""

    @property
    @functools.lru_cache(maxsize=1)
    def precincts(self):
        results_d = {}
        
        response = self.session.get(self.RESULTS_URL,
                                    params = {'election': self.elec_code,
                                              'race': self.number})
        page = lxml.html.fromstring(response.text)

        tables = page.xpath('//table')

        total = tables.pop(0)
        header_row = total.xpath('./tr')[0]
        keys = ['precinct']
        for cell in header_row.xpath('./td//text()'):
            keys.append(cell.strip().replace("''", "'"))

        for table in tables:
            rows = table.xpath('./tr')
            ward = rows.pop(0).xpath('./td//text()')[0]
            ward_num = int(ward.split()[-1])
            rows.pop(0) # ignore repeated header row
            for row in rows:
                votes = {}
                for key, cell in zip(keys, row.xpath('./td//text()')):
                    if cell == 'Total': # ignore ward subtotals
                        break
                    if '%' in key or key == 'Votes': # ignore derived vars
                        continue
                    votes[key] = int(cell.strip().replace(',', ''))
                else:
                    precinct = votes.pop('precinct')
                    results_d[(ward_num, precinct)] = votes

        return results_d

    @property
    @functools.lru_cache(maxsize=1)
    def wards(self):
        results_d = collections.defaultdict(lambda: collections.defaultdict(int))
        for (ward, precinct), precinct_votes in self.precincts.items():
            for choice, votes in precinct_votes.items():
                results_d[ward][choice] += votes

        results_d = dict(results_d)
        for k, v in results_d.items():
            results_d[k] = dict(v)

        return results_d

    @property
    @functools.lru_cache(maxsize=1)
    def total(self):
        results_d = collections.defaultdict(int)
        for precinct_votes in self.precincts.values():
            for choice, votes in precinct_votes.items():
                results_d[choice] += votes

        return dict(results_d)

            

def elections(session=None):
    '''List all available elections'''

    election_url = 'https://chicagoelections.com/en/election-results.html'

    if session is None:
        session = requests.Session()
    else:
        session = session
    
    response = session.get(election_url)
    page = lxml.html.fromstring(response.text)

    election_links = page.xpath("//a[starts-with(@href, 'election-results.asp?election=')]")

    elex = {}

    for link in election_links:
        name = link.text
        election_code = link.get('href').split('=')[-1]
        elex[name] = Election(election_code, name, session)

    return elex
        
