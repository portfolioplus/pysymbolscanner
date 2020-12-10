#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pysymbolscanner
  Copyright 2020 Slash Gordon
  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
import unittest
from unittest import mock
from pysymbolscanner.wiki import (
    get_infobox,
    get_merged_infobox,
    get_wiki_infobox,
)
from pysymbolscanner.infobox import get_country
import json
import os
from pysymbolscanner.scanner import SymbolScanner
from pysymbolscanner.index_definitions import Indices
from pytickersymbols import Statics


def create_test_data():
    infobox_dict = {
        'Alphabet': {
            'en': None,
            'de': None,
            'fr': None,
            'es': None,
        },
        'BASF': {
            'en': None,
            'de': None,
            'fr': None,
            'es': None,
        },
        'Amadeus FiRe': {
            'en': None,
            'de': None,
        },
        'BMW': {
            'en': None,
            'de': None,
            'fr': None,
            'es': None,
        },
        'CaixaBank': {
            'es': None,
        },
    }
    for page in infobox_dict:
        for lang in infobox_dict[page]:
            infobox = get_wiki_infobox(page, [lang])
            infobox_dict[page][lang] = infobox[0] if infobox else None
    with open('tests/test_data.json', 'w') as fp:
        json.dump(infobox_dict, fp)


def mock_get_wiki_info_box(page, lang_codes=['en', 'de', 'es', 'fr']):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, 'test_data.json')) as json_file:
        data = json.load(json_file)
        if page not in data:
            return None
        wiki_page = data[page]
        for lang in lang_codes:
            if lang in wiki_page:
                return wiki_page[lang], lang
    return None


class TestWiki(unittest.TestCase):
    @mock.patch(
        'pysymbolscanner.wiki.get_wiki_infobox',
        side_effect=mock_get_wiki_info_box,
    )
    def test_infobox(self, mock_func):
        """
        Test wiki infobox
        :return:
        """
        items_google = get_infobox('Alphabet')
        self.assertEqual(items_google.name, 'Alphabet Inc.')
        self.assertEqual(items_google.founded, 2015)
        self.assertEqual(items_google.employees, 127498)
        self.assertEqual(items_google.location, 'United States')
        self.assertEqual(len(items_google.isins), 2)
        self.assertEqual(len(items_google.symbols), 2)
        self.assertIn('Conglomerate', items_google.industry)
        items_basf = get_infobox('BASF')
        self.assertEqual(items_basf.name, 'BASF SE')
        self.assertEqual(items_basf.founded, 1865)
        self.assertEqual(items_basf.employees, 117628)
        self.assertEqual(items_basf.location, 'Germany')
        self.assertEqual(len(items_basf.isins), 0)
        self.assertEqual(len(items_basf.symbols), 1)
        self.assertIn('Chemicals', items_basf.industry)
        items_bmw = get_infobox('BMW')
        self.assertEqual(items_bmw.name, 'Bayerische Motoren Werke AG')
        self.assertEqual(items_bmw.founded, 1916)
        self.assertEqual(items_bmw.employees, 133778)
        self.assertEqual(items_bmw.location, 'Germany')
        self.assertEqual(len(items_bmw.isins), 0)
        self.assertEqual(len(items_bmw.symbols), 1)
        self.assertIn('Automotive', items_bmw.industry)

    @mock.patch(
        'pysymbolscanner.wiki.get_wiki_infobox',
        side_effect=mock_get_wiki_info_box,
    )
    def test_merged_infoboxes(self, mock_func):
        """
        Test wiki infobox
        :return:
        """
        items_caixa = get_merged_infobox('CaixaBank', ['es'])
        self.assertEqual(items_caixa.name, 'CaixaBank, S.A.')
        self.assertEqual(items_caixa.founded, 2011)
        self.assertEqual(items_caixa.employees, 37440)
        self.assertEqual(items_caixa.location, 'Spain')
        self.assertEqual(len(items_caixa.isins), 1)
        items_bmw = get_merged_infobox('BMW', ['de', 'en'])
        self.assertEqual(items_bmw.name, 'Bayerische Motoren Werke AG')
        self.assertEqual(items_bmw.founded, 1916)
        self.assertEqual(items_bmw.employees, 133778)
        self.assertEqual(items_bmw.location, 'Germany')
        self.assertEqual(len(items_bmw.isins), 1)
        self.assertEqual(len(items_bmw.symbols), 1)
        self.assertIn('Automotive', items_bmw.industry)
        amadeus = get_merged_infobox('Amadeus FiRe', ['de', 'en'])
        self.assertEqual(amadeus.name, 'Amadeus FiRe AG')
        self.assertEqual(amadeus.founded, 2003)
        self.assertEqual(amadeus.employees, 2907)
        self.assertEqual(amadeus.location, 'Germany')
        self.assertEqual(len(amadeus.isins), 1)
        self.assertEqual(len(amadeus.symbols), 0)

    def test_get_country(self):
        """
        Test country detection
        :return:
        """
        country = get_country('en', None)
        self.assertIsNone(country)
        country = get_country('en', 'Deutschland')
        self.assertIsNone(country)
        country = get_country('en', 'Berlin, Germany')
        self.assertIsNotNone(country)
        self.assertEqual(len(country), 3)
        country, code, code2 = country
        self.assertEqual(country, 'Germany')
        self.assertEqual(code, 'DE')
        self.assertEqual(code2, 'DEU')
        country = get_country('de', 'Berlin, Deutschland')
        self.assertIsNotNone(country)
        self.assertEqual(len(country), 3)
        country, code, code2 = country
        self.assertEqual(country, 'Germany')
        self.assertEqual(code, 'DE')
        self.assertEqual(code2, 'DEU')

    def test_1(self):
        box = get_merged_infobox('Kingfisher', ['de', 'en'])
        self.assertEqual(box, None)

    def test_2(self):
        scannner = SymbolScanner(False)
        index = scannner.worker_index(
            (
                Statics.Indices.RU_MOEX,
                Indices.symbol_source_dict[Statics.Indices.RU_MOEX],
            )
        )
        self.assertEqual(index, None)


# Did not find any wikipedia data for Befesa
# Did not find any wikipedia data for Rosagro
# Did not find any wikipedia data for OJSC Magnit
# Did not find any wikipedia data for SFI
# Did not find any wikipedia data for Kingfisher
# Did not find any wikipedia data for Kojamo
# Did not find any wikipedia data for Elisa
# Did not find any wikipedia data for Alphabet Inc. (Class A)
# Did not find any wikipedia data for Mondelēz International
# Did not find any wikipedia data for Genfit
# Did not find any wikipedia data for Mondelēz International
# Did not find any wikipedia data for Anthem
# Did not find any wikipedia data for Alphabet Inc. (Class A)
# Did not find any wikipedia data for Corning Inc.
# Did not find any wikipedia data for Edison Int'l
# Did not find any wikipedia data for Discovery, Inc. (Class A)
# Did not find any wikipedia data for Fox Corporation (Class B)
# Did not find any wikipedia data for Mastercard Inc.
# Did not find any wikipedia data for Norfolk Southern Corp.
# Did not find any wikipedia data for Discovery, Inc. (Class C)
# Did not find any wikipedia data for PACCAR Inc.
# Did not find any wikipedia data for KeyCorp
# Did not find any wikipedia data for Lowe's Cos.
# Did not find any wikipedia data for Lilly (Eli) & Co.
# Did not find any wikipedia data for Marriott Int'l.
# Did not find any wikipedia data for Pool Corporation
# Did not find any wikipedia data for QUALCOMM Inc.
# Did not find any wikipedia data for Schlumberger Ltd.
# Did not find any wikipedia data for Svenska Kullagerfabriken (B)
# Did not find any wikipedia data for Hexagon (B)
# Did not find any wikipedia data for Aedifica
# Did not find any wikipedia data for arGEN-X
# Did not find any wikipedia data for WDP
# Did not find any wikipedia data for DSM
# Did not find any match for MOEX - Rosagro
# Did not find any match for SDAX - ADVA Optical Networking SE
# Did not find any match for OMX Helsinki 25 - Kemira Oyj
# Did not find any match for MOEX - PJSC Acron
# Did not find any match for EURO STOXX 50 - Anheuser-Busch Companies, LLC
# Did not find any match for SDAX - Amadeus FiRe AG
# Did not find any match for OMX Helsinki 25 - Kojamo
# Did not find any match for IBEX 35 - ENAIRE
# Did not find any match for DOW JONES - Dow Inc.
# Did not find any match for MOEX - Lenta
# Did not find any match for FTSE 100 - AVEVA Group plc
# Did not find any match for OMX Helsinki 25 - Neles Oyj
# Did not find any match for FTSE 100 - B&M
# Did not find any match for MOEX - Dixy Chicken
# Did not find any match for SDAX - Borussia Dortmund GmbH & Co. KGaA
# Did not find any match for IBEX 35 - Banco Santander, S.A.
# Did not find any match for OMX Helsinki 25 - Nokian Tyres plc
# Did not find any match for MOEX - OJSC LSR Group
# Did not find any match for EURO STOXX 50 - Enel S.p.A.
# Did not find any match for OMX Helsinki 25 - TietoEVRY
# Did not find any match for SDAX - Dermapharm Holding SE
# Did not find any match for EURO STOXX 50 - Eni S.p.A.
# Did not find any match for MOEX - OJSC Mosenergo
# Did not find any match for S&P 100 - DuPont de Nemours, Inc.
# Did not find any match for CAC Mid 60 - Groupe ADP
# Did not find any match for CAC Mid 60 - Air France-KLM Group SA
# Did not find any match for S&P 100 - Dow Inc.
# Did not find any match for EURO STOXX 50 - Intesa Sanpaolo
# Did not find any match for SDAX - Eckert & Ziegler Strahlen- und Medizintechnik AG
# Did not find any match for MOEX - OJSC Novorossiysk Commercial Sea Port
# Did not find any match for CAC Mid 60 - ALD Automotive
# Did not find any match for EURO STOXX 50 - LVMH Moët Hennessy Louis Vuitton
# Did not find any match for S&P 100 - General Dynamics Corporation
# Did not find any match for CAC Mid 60 - ALTEN
# Did not find any match for FTSE 100 - GVC Holdings plc
# Did not find any match for EURO STOXX 50 - Munich Re
# Did not find any match for CAC Mid 60 - Amundi
# Did not find any match for SDAX - HORNBACH Baumarkt AG
# Did not find any match for DAX - Henkel AG & Co. KGaA
# Did not find any match for MOEX - PAO Rosseti
# Did not find any match for FTSE 100 - HomeServe plc
# Did not find any match for CAC Mid 60 - Bank BIC Namibia Limited
# Did not find any match for MOEX - SFI
# Did not find any match for CAC Mid 60 - BioMérieux
# Did not find any match for MOEX - PJSC Sberbank
# Did not find any match for CAC Mid 60 - Bolloré
# Did not find any match for SDAX - Instone Real Estate Group AG
# Did not find any match for FTSE 100 - Intermediate Capital Group plc
# Did not find any match for MOEX - PJSC Sberbank
# Did not find any match for CAC Mid 60 - CGG
# Did not find any match for FTSE 100 - International Airlines Group
# Did not find any match for CAC Mid 60 - CNP Assurances
# Did not find any match for S&P 100 - Lockheed Martin Corporation
# Did not find any match for FTSE 100 - JD Sports Fashion plc
# Did not find any match for CAC Mid 60 - Coface
# Did not find any match for S&P 100 - New test edit for create new uak account
# Did not find any match for CAC Mid 60 - Covivio
# Did not find any match for S&P 100 - Mondelēz International
# Did not find any match for SDAX - LPKF Laser & Electronics AG
# Did not find any match for CAC Mid 60 - Dassault Aviation
# Did not find any match for FTSE 100 - 20 Fenchurch Street
# Did not find any match for TECDAX - Eckert & Ziegler Strahlen- und Medizintechnik AG
# Did not find any match for SDAX - New Work SE
# Did not find any match for CAC Mid 60 - DBV Technologies
# Did not find any match for CAC Mid 60 - Elior Group
# Did not find any match for TECDAX - LPKF Laser & Electronics AG
# Did not find any match for FTSE 100 - M&G
# Did not find any match for CAC Mid 60 - Eramet
# Did not find any match for NASDAQ 100 - CDW Corporation
# Did not find any match for Switzerland 20 - Partners Group
# Did not find any match for TECDAX - New Work SE
# Did not find any match for CAC Mid 60 - Eurazeo
# Did not find any match for S&P 100 - PepsiCo, Inc.
# Did not find any match for CAC 40 - Essilor
# Did not find any match for Switzerland 20 - Swiss Reinsurance Company Ltd
# Did not find any match for SDAX - SNP Schneider-Neureither & Partner SE
# Did not find any match for CAC Mid 60 - Eurofins Scientific
# Did not find any match for FTSE 100 - NatWest Group plc
# Did not find any match for CAC Mid 60 - Euronext
# Did not find any match for SDAX - STRATEC SE
# Did not find any match for CAC Mid 60 - Europcar Mobility Group
# Did not find any match for TECDAX - TeamViewer AG
# Did not find any match for NASDAQ 100 - CoStar Group, Inc.
# Did not find any match for FTSE 100 - Pennon Group plc
# Did not find any match for CAC Mid 60 - Eutelsat
# Did not find any match for SDAX - Traton Group
# Did not find any match for TECDAX - VARTA AG
# Did not find any match for NASDAQ 100 - DexCom, Inc.
# Did not find any match for CAC Mid 60 - Française des Jeux
# Did not find any match for CAC 40 - PSA
# Did not find any match for CAC Mid 60 - Groupe Casino
# Did not find any match for SDAX - ZEAL Network SE
# Did not find any match for CAC Mid 60 - Groupe Fnac Darty
# Did not find any match for CAC Mid 60 - Genfit
# Did not find any match for BEL 20 - Aedifica
# Did not find any match for S&P 500 - Alliant Energy Corporation
# Did not find any match for CAC Mid 60 - Gaztransport & Technigaz
# Did not find any match for CAC Mid 60 - Icade
# Did not find any match for BEL 20 - AB InBev
# Did not find any match for CAC 40 - Thales
# Did not find any match for CAC Mid 60 - Iliad
# Did not find any match for S&P 500 - Amcor plc
# Did not find any match for CAC Mid 60 - Imerys
# Did not find any match for NASDAQ 100 - lululemon athletica inc.
# Did not find any match for CAC Mid 60 - Ipsen Group
# Did not find any match for BEL 20 - Galápagos Islands
# Did not find any match for CAC Mid 60 - Ipsos
# Did not find any match for OMX Stockholm 30 - Svenska Kullagerfabriken (B)
# Did not find any match for NASDAQ 100 - Mercado Libre, Inc.
# Did not find any match for BEL 20 - GBL
# Did not find any match for FTSE 100 - SSE plc
# Did not find any match for CAC Mid 60 - JCDecaux
# Did not find any match for CAC Mid 60 - KORIAN
# Did not find any match for NASDAQ 100 - Mondelēz International
# Did not find any match for CAC Mid 60 - Lagardère
# Did not find any match for MDAX - Knorr-Bremse Aktiengesellschaft
# Did not find any match for CAC Mid 60 - Maisons du Monde
# Did not find any match for AEX - Galápagos Islands
# Did not find any match for CAC Mid 60 - Mercialys
# Did not find any match for BEL 20 - WDP
# Did not find any match for CAC Mid 60 - Métropole TV
# Did not find any match for CAC Mid 60 - Nexans
# Did not find any match for NASDAQ 100 - PepsiCo, Inc.
# Did not find any match for CAC Mid 60 - Nexity
# Did not find any match for AEX - Prosus N.V.
# Did not find any match for CAC Mid 60 - Orpea-Gruppe
# Did not find any match for NASDAQ 100 - Seagen Inc.
# Did not find any match for MDAX - Ströer SE & Co. KGaA
# Did not find any match for CAC Mid 60 - Plastic Omnium
# Did not find any match for NASDAQ 100 - Splunk Inc.
# Did not find any match for MDAX - TeamViewer AG
# Did not find any match for CAC Mid 60 - Quadient
# Did not find any match for CAC Mid 60 - Rémy Cointreau
# Did not find any match for S&P 500 - Bio-Rad Laboratories, Inc.
# Did not find any match for CAC Mid 60 - Rexel
# Did not find any match for MDAX - VARTA AG
# Did not find any match for NASDAQ 100 - Trip.com Group Limited
# Did not find any match for CAC Mid 60 - Groupe SEB
# Did not find any match for NASDAQ 100 - United Airlines Holdings, Inc.
# Did not find any match for CAC Mid 60 - Soitec
# Did not find any match for CAC Mid 60 - Sopra Steria
# Did not find any match for CAC Mid 60 - SPIE
# Did not find any match for NASDAQ 100 - Workday, Inc.
# Did not find any match for CAC Mid 60 - Tarkett
# Did not find any match for NASDAQ 100 - Xcel Energy Inc.
# Did not find any match for CAC Mid 60 - TF1 Group
# Did not find any match for CAC Mid 60 - Trigano
# Did not find any match for NASDAQ 100 - Zoom Video Communications, Inc.
# Did not find any match for CAC Mid 60 - Vallourec
# Did not find any match for S&P 500 - Carrier Global Corporation
# Did not find any match for CAC Mid 60 - Verallia
# Did not find any match for S&P 500 - Catalent, Inc.
# Did not find any match for CAC Mid 60 - Virbac
# Did not find any match for S&P 500 - Cboe Global Markets, Inc.
# Did not find any match for CAC Mid 60 - Wendel
# Did not find any match for S&P 500 - CDW Corporation
# Did not find any match for S&P 500 - DexCom, Inc.
# Did not find any match for S&P 500 - Domino's Pizza, Inc.
# Did not find any match for S&P 500 - Dow Inc.
# Did not find any match for S&P 500 - DuPont de Nemours, Inc.
# Did not find any match for S&P 500 - Equinix, Inc.
# Did not find any match for S&P 500 - Etsy, Inc.
# Did not find any match for S&P 500 - F5, Inc.
# Did not find any match for S&P 500 - General Dynamics Corporation
# Did not find any match for S&P 500 - Globe Life Inc.
# Did not find any match for S&P 500 - Healthpeak Properties, Inc.
# Did not find any match for S&P 500 - Howmet Aerospace Inc.
# Did not find any match for S&P 500 - IDEX Corporation
# Did not find any match for S&P 500 - L3Harris Technologies, Inc.
# Did not find any match for S&P 500 - Las Vegas Sands Corporation
# Did not find any match for S&P 500 - Leidos Holdings, Inc.
# Did not find any match for S&P 500 - Lilly (Eli) & Co.
# Did not find any match for S&P 500 - Live Nation Entertainment, Inc.
# Did not find any match for S&P 500 - Lockheed Martin Corporation
# Did not find any match for S&P 500 - Lowe's Cos.
# Did not find any match for S&P 500 - MarketAxess Holdings Inc.
# Did not find any match for S&P 500 - Marriott Int'l.
# Did not find any match for S&P 500 - McCormick & Company
# Did not find any match for S&P 500 - Molson Coors Beverage Company
# Did not find any match for S&P 500 - Northrop Grumman Corporation
# Did not find any match for S&P 500 - NortonLifeLock Inc.
# Did not find any match for S&P 500 - NVR, Inc.
# Did not find any match for S&P 500 - Old Dominion Freight Line, Inc.
# Did not find any match for S&P 500 - Otis Worldwide Corporation
# Did not find any match for S&P 500 - PepsiCo, Inc.
# Did not find any match for S&P 500 - Pool Corporation
# Did not find any match for S&P 500 - Principal Financial Group, Inc.
# Did not find any match for S&P 500 - Regency Centers Corporation
# Did not find any match for S&P 500 - ServiceNow, Inc.
# Did not find any match for S&P 500 - Teledyne Technologies Incorporated
# Did not find any match for S&P 500 - Teradyne, Inc.
# Did not find any match for S&P 500 - Textron Inc.
# Did not find any match for S&P 500 - Truist Financial Corporation
# Did not find any match for S&P 500 - United Airlines Holdings, Inc.
# Did not find any match for S&P 500 - VF Corporation
# Did not find any match for S&P 500 - ViacomCBS Inc.
# Did not find any match for S&P 500 - Viatris
# Did not find any match for S&P 500 - Teletrac
# Did not find any match for S&P 500 - W. R. Berkley Corporation
# Did not find any match for S&P 500 - Westinghouse Air Brake Technologies Corporation
# Did not find any match for S&P 500 - West Pharmaceutical Services, Inc.
# Did not find any match for S&P 500 - Xcel Energy Inc.
if __name__ == "__main__":
    unittest.main()
