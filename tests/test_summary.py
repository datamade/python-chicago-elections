# -*- coding=utf-8 -*-
import os.path
from unittest import TestCase

from chi_elections.summary import (FixedWidthField, ResultParser, SummaryClient,
        SummaryParser)

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
    'data')
SUMMARY_TEST_FILENAME = os.path.join(TEST_DATA_DIR, 'results', 'ap',
    'summary.txt')

class ParserTestCase(TestCase):

    def setUp(self):
        self.parser = SummaryParser()

    def test_parse(self):
        with open(SUMMARY_TEST_FILENAME, 'r') as f:
            self.parser.parse(f.read())
            self.assertEqual(len(self.parser.races), 198)
            print(self.parser.races)

            # mayor = next(r for r in self.parser.races if r.name == "Mayor")
            # self.assertEqual(len(mayor.candidates), 5)
            #
            # rahm = next(c for c in mayor.candidates
            #             if c.full_name == "RAHM EMANUEL")
            # self.assertEqual(rahm.vote_total, 0)

           
# class FixedWidthFieldTestCase(TestCase):
    # def test_parse(self):
    #     line = "0010001206900000000000NON       Mayor                                                   RAHM EMANUEL                          City Of Chicago          001"
    #     field = FixedWidthField(0, 3, transform=int)
    #     parsed = field.parse(line)
    #     self.assertEqual(parsed, 1)
    #     field = FixedWidthField(22, 3)
    #     parsed = field.parse(line)
    #     self.assertEqual(parsed, "NON")
    #     field = FixedWidthField(32, 56)
    #     parsed = field.parse(line)
    #     self.assertEqual(parsed, "Mayor")


class ResultParserTestCase(TestCase):
    def test_parse_line(self):
        parser = ResultParser()
        line = "2000060001200000000000000722450000000U.S. Representative, 2nd District                                     Robin Kelly                                       Democratic                                        DEMCONGRESS                                          000040007801"
        result = parser.parse_line(line)
        self.assertEqual(result['completed_precincts'], 0)
        self.assertEqual(result['total_registration'], 72245)
        self.assertEqual(result['vote_for'], 0)
        self.assertEqual(result['race_name'], "U.S. Representative, 2nd District")
        self.assertEqual(result['candidate_name'], "Robin Kelly")
        self.assertEqual(result['party'], "Democratic")
        self.assertEqual(result['race_type'], "DEMCONGRESS")
        self.assertEqual(result['precincts_total'], 78)

    # def test_parse_line_no_text(self):
    #     parser = ResultParser()
    #     line = "0010001206900000000000"
    #     result = parser.parse_line(line)
    #     self.assertEqual(result['contest_code'], 10)
    #     self.assertEqual(result['candidate_number'], 1)
    #     self.assertEqual(result['precincts_total'], 2069)
    #     self.assertEqual(result['vote_total'], 0)
    #     self.assertEqual(result['precincts_reporting'], 0)
    #     self.assertEqual(result['party'], "")
    #     self.assertEqual(result['race_name'], "")
    #     self.assertEqual(result['candidate_name'], "")
    #     self.assertEqual(result['reporting_unit_name'], "")
    #     self.assertEqual(result['vote_for'], None)

    # def test_parse_line_utf8(self):
    #     parser = ResultParser()
    #     line = "0023012034800000000000DEM       Delegate, National Convention 4th DEM                   Álvaro R. Obregón (Sanders)           4th Congressional Distric005"
    #     result = parser.parse_line(line)
    #     self.assertEqual(result['contest_code'], 23)
    #     self.assertEqual(result['candidate_number'], 12)
    #     self.assertEqual(result['precincts_total'], 348)
    #     self.assertEqual(result['vote_total'], 0)
    #     self.assertEqual(result['precincts_reporting'], 0)
    #     self.assertEqual(result['party'], "DEM")
    #     self.assertEqual(result['race_name'], "Delegate, National Convention 4th DEM")
    #     self.assertEqual(result['candidate_name'], u"Álvaro R. Obregón (Sanders)")
    #     self.assertEqual(result['reporting_unit_name'], "4th Congressional Distric")
    #     self.assertEqual(result['vote_for'], 5)


# class SummaryClientTestCase(TestCase):
#     @responses.activate
#     def test_fetch(self):
#         client = SummaryClient()
#         with open(SUMMARY_TEST_FILENAME) as f:
#             response_body = f.read()
#             responses.add(responses.GET, client.get_url(), body=response_body,
#                 content_type='text/plain')    
#             client.fetch() 
#             self.assertEqual(len(client.races), 98)
#
#             mayor = next(r for r in client.races if r.name == "Mayor")
#             self.assertEqual(len(mayor.candidates), 5)
#
#             rahm = next(c for c in mayor.candidates
#                         if c.full_name == "RAHM EMANUEL")
#             self.assertEqual(rahm.vote_total, 0)
