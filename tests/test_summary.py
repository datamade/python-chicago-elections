# -*- coding=utf-8 -*-
import os.path
from unittest import TestCase

import responses

from chi_elections.summary import (FixedWidthField, ResultParser, SummaryClient,
        SummaryParser)

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
    'data')
SUMMARY_TEST_FILENAME = os.path.join(TEST_DATA_DIR, 'results', 'ap',
    'SummaryExport.txt')

class ParserTestCase(TestCase):

    def setUp(self):
        self.parser = SummaryParser()

    def test_parse(self):
        with open(SUMMARY_TEST_FILENAME, 'r') as f:
            self.parser.parse(f.read())
            self.assertEqual(len(self.parser.races), 88)

            mayor = next(r for r in self.parser.races if r.name == "Mayor")
            self.assertEqual(len(mayor.candidates), 9)

            lori = next(c for c in mayor.candidates
                        if c.full_name == "LORI E. LIGHTFOOT")
            self.assertEqual(lori.vote_total, 0)

           
class FixedWidthFieldTestCase(TestCase):
    def test_parse(self):
        line = "0010001206900000000000NON       Mayor                                                   RAHM EMANUEL                          City Of Chicago          001"
        field = FixedWidthField(0, 3, transform=int)
        parsed = field.parse(line)
        self.assertEqual(parsed, 1)
        field = FixedWidthField(22, 3)
        parsed = field.parse(line)
        self.assertEqual(parsed, "NON")
        field = FixedWidthField(32, 56)
        parsed = field.parse(line)
        self.assertEqual(parsed, "Mayor")



class ResultParserTestCase(TestCase):
    def test_parse_line(self):
        parser = ResultParser()
        line = "2000010000700000000000012354380000000Mayor                                                                 LORI E. LIGHTFOOT                                                                                      MUNICIPAL                                         000080129101"
        result = parser.parse_line(line)
        self.assertEqual(result['contest_code'], 1)
        self.assertEqual(result['candidate_number'], 7)
        self.assertEqual(result['precincts_total'], 1291)
        self.assertEqual(result['vote_total'], 0)
        self.assertEqual(result['precincts_reporting'], 0)
        self.assertEqual(result['party'], "")
        self.assertEqual(result['race_name'], "Mayor")
        self.assertEqual(result['candidate_name'], "LORI E. LIGHTFOOT")
        self.assertEqual(result['reporting_unit_name'], "MUNICIPAL")
        self.assertEqual(result['vote_for'], 1)

    def test_parse_line_utf8(self):
        parser = ResultParser()
        line = "2000340014700000000000000191530000000Alderperson 31st Ward                                                 ESTEBAN BURGOA ONTAÑON                                                                                 WARD                                              000090002301"
        result = parser.parse_line(line)
        self.assertEqual(result['contest_code'], 34)
        self.assertEqual(result['candidate_number'], 147)
        self.assertEqual(result['precincts_total'], 23)
        self.assertEqual(result['vote_total'], 0)
        self.assertEqual(result['precincts_reporting'], 0)
        self.assertEqual(result['party'], "")
        self.assertEqual(result['race_name'], "Alderperson 31st Ward")
        self.assertEqual(result['candidate_name'], u"ESTEBAN BURGOA ONTAÑON")
        self.assertEqual(result['reporting_unit_name'], "WARD")
        self.assertEqual(result['vote_for'], 1)


class SummaryClientTestCase(TestCase):
    @responses.activate
    def test_fetch(self):
        client = SummaryClient()
        with open(SUMMARY_TEST_FILENAME) as f:
            response_body = f.read()
            responses.add(responses.GET, client.get_url(), body=response_body,
                content_type='text/plain')    
            client.fetch() 
            self.assertEqual(len(client.races), 88)

            mayor = next(r for r in client.races if r.name == "Mayor")
            self.assertEqual(len(mayor.candidates), 9)

            lori = next(c for c in mayor.candidates
                        if c.full_name == "LORI E. LIGHTFOOT")
            self.assertEqual(lori.vote_total, 0)
