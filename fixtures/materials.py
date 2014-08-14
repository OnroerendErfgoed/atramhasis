# -*- coding: utf-8 -*-
'''
Testdata cotaining materials: concrete, glass, metal, silex, ...

.. versionadded:: 0.2.0
'''

from __future__ import unicode_literals

from skosprovider.providers import DictionaryProvider
from skosprovider.uri import UriPatternGenerator

mdata = [
        {'broader': [0], 'narrower': [2, 5, 6], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'aardewerk'}, {'type': 'altLabel', 'language': 'nl', 'label': 'ceramiek'}, {'type': 'altLabel', 'language': 'nl', 'label': 'keramiek'}], 'type': 'concept', 'id': 1, 'related': []},
        {'broader': [8], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'aluminium'}], 'type': 'concept', 'id': 48, 'related': []},
        {'broader': [32], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'amber'}, {'type': 'altLabel', 'language': 'nl', 'label': 'barnsteen'}], 'type': 'concept', 'id': 33, 'related': []},
        {'broader': [0], 'narrower': [39], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'beton'}, {'type': 'prefLabel', 'language': 'en', 'label': 'concrete'}, {'type': 'prefLabel', 'language': 'fr', 'label': 'béton'}], 'type': 'concept', 'id': 38, 'related': []},
        {'broader': [9], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'bladgoud'}], 'type': 'concept', 'id': 10, 'related': []},
        {
            'broader': [21],
            'narrower': [],
            'notes': [
                {
                    'type': 'definition',
                    'language': 'nl',
                    'note': 'Bont is een gelooide dierlijke huid, dicht bezet met haren. Het wordt voornamelijk gebruikt voor het maken van kleding.'
                }
            ], 
            'labels': [
                {'type': 'prefLabel', 'language': 'nl', 'label': 'bont'},
                {'type': 'prefLabel', 'language': 'en', 'label': 'fur'}
            ], 
            'type': 'concept', 
            'id': 23, 
            'related': []
        },
        {'broader': [21], 'narrower': [25, 26], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'botmateriaal'}], 'type': 'concept', 'id': 24, 'related': []},
        {
            'broader': [13],
            'narrower': [],
            'notes': [],
            'labels': [
                {'type': 'prefLabel', 'language': 'nl', 'label': 'brons'},
                {'type': 'prefLabel', 'language': 'fr', 'label': 'bronze'},
                {'type': 'prefLabel', 'language': 'en', 'label': 'bronze'},
            ], 
            'type': 'concept',
            'id': 14,
            'related': []
        },
        {
            'broader': [0],
            'narrower': [],
            'notes': [
                {
                    'type': 'definition',
                    'language': 'nl',
                    'note': 'Cement is de benaming voor verschillende stoffen die een snel verhardend bindmiddel voor bouwwerken (mortel) opleveren.'
                }
            ],
            'labels': [
                {'type': 'prefLabel', 'language': 'nl', 'label': 'cement'}
            ], 
            'type': 'concept',
            'id': 49,
            'related': []
        },
        {'broader': [24], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'dierlijk botmateriaal'}], 'type': 'concept', 'id': 25, 'related': []},
        {'broader': [38], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'gewapend beton'}, {'type': 'prefLabel', 'language': 'en', 'label': 'reinforced concrete'}, {'type': 'prefLabel', 'language': 'fr', 'label': 'béton armé'}], 'type': 'concept', 'id': 39, 'related': []},
        {'broader': [21], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'gewei'}], 'type': 'concept', 'id': 27, 'related': []},
        {'broader': [0], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'glas'}], 'type': 'concept', 'id': 7, 'related': []},
        {
            'broader': [8],
            'narrower': [10],
            'notes': [],
            'labels': [
                {'type': 'prefLabel', 'language': 'nl', 'label': 'goud'},
                {'type': 'prefLabel', 'language': 'en', 'label': 'gold'},
                {'type': 'prefLabel', 'language': 'fr', 'label': 'or'}
            ], 
            'type': 'concept', 
            'id': 9, 
            'related': []
        },
        {'broader': [21], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'hoorn/hoornpitten'}], 'type': 'concept', 'id': 28, 'related': []},
        {'broader': [32], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'hout'}], 'type': 'concept', 'id': 35, 'related': []},
        {'broader': [32], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'houtskool'}], 'type': 'concept', 'id': 36, 'related': []},
        {'broader': [21], 'narrower': [30], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'huid'}], 'type': 'concept', 'id': 29, 'related': []},
        {'broader': [8], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'ijzer'}], 'type': 'concept', 'id': 11, 'related': []},
        {'broader': [8], 'narrower': [13], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'koper'}], 'type': 'concept', 'id': 12, 'related': []},
        {'broader': [12], 'narrower': [14, 15], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'koperlegeringen'}], 'type': 'concept', 'id': 13, 'related': []},
        {'broader': [0], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'kunststof'}], 'type': 'concept', 'id': 20, 'related': []},
        {'broader': [43], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'kwartsiet van Tienen'}], 'type': 'concept', 'id': 44, 'related': []},
        {'broader': [42], 'narrower': [44, 45], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'kwartsitisch lithisch materiaal'}], 'type': 'concept', 'id': 43, 'related': []},
        {'broader': [29], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'leer'}], 'type': 'concept', 'id': 30, 'related': []},
        {'broader': [40], 'narrower': [43, 46], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'lithisch materiaal'}], 'type': 'concept', 'id': 42, 'related': []},
        {'broader': [8], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'lood'}], 'type': 'concept', 'id': 16, 'related': []},
        {'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'Materiaal'}], 'type': 'collection', 'id': 0, 'members': [1, 7, 8, 20, 21, 31, 38, 40, 49, 50]},
        {'broader': [24], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'menselijk botmateriaal'}], 'type': 'concept', 'id': 26, 'related': []},
        {'broader': [13], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'messing'}], 'type': 'concept', 'id': 15, 'related': []},
        {'broader': [0], 'narrower': [9, 11, 12, 16, 17, 18, 19, 48], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'metaal'}], 'type': 'concept', 'id': 8, 'related': []},
        {'broader': [40], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'natuursteen'}], 'type': 'concept', 'id': 41, 'related': []},
        {'broader': [0], 'narrower': [23, 24, 27, 28, 29, 32], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'organisch materiaal'}], 'type': 'concept', 'id': 21, 'related': []},
        {'broader': [1], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'pijpaarde'}], 'type': 'concept', 'id': 2, 'related': []},
        {'broader': [21], 'narrower': [33, 35, 36, 37], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'plantaardig materiaal'}], 'type': 'concept', 'id': 32, 'related': []},
        {'broader': [0], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'pleister'}], 'type': 'concept', 'id': 50, 'related': []},
        {'broader': [1], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'porselein'}], 'type': 'concept', 'id': 5, 'related': []},
        {'broader': [0], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'schelp'}], 'type': 'concept', 'id': 31, 'related': []},
        {'broader': [42], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'silex'}, {'type': 'altLabel', 'language': 'nl', 'label': 'vuursteen'}], 'type': 'concept', 'id': 46, 'related': []},
        {'broader': [8], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'staal'}], 'type': 'concept', 'id': 17, 'related': []},
        {'broader': [0], 'narrower': [41, 42], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'steen'}], 'type': 'concept', 'id': 40, 'related': []},
        {'broader': [1], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'steengoed'}], 'type': 'concept', 'id': 6, 'related': []},
        {'broader': [32], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'textiel'}], 'type': 'concept', 'id': 37, 'related': []},
        {'broader': [8], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'tin'}], 'type': 'concept', 'id': 18, 'related': []},
        {
            'broader': [43],
            'narrower': [],
            'notes': [
                {
                    'type': 'defintion', 
                    'language': 'nl',
                    'note': 'Wommersomkwartsiet vertoont een textuur van hoekige kwartskorrels in een fijnkorrelig kwartscement ingebed. Deze gesteentesoort komt schijnbaar alleen voor in Wommersom, nabij Tienen. Het vertoont enige gelijkenis met silex en werd alsdusdanig ook gebruikt om prehistorische werktuigen te maken.'
                }
            ], 
            'labels': [
                {'type': 'prefLabel', 'language': 'nl', 'label': 'wommersomkwartsiet'},
                {'type': 'prefLabel', 'language': 'fr', 'label': 'grès quartzite de Wommersom'}
            ], 
            'type': 'concept',
            'id': 45,
            'related': []
        },
        {
            'broader': [8],
            'narrower': [],
            'notes': [],
            'labels': [
                {'type': 'prefLabel', 'language': 'nl', 'label': 'zilver'},
                {'type': 'prefLabel', 'language': 'en', 'label': 'silver'},
                {'type': 'prefLabel', 'language': 'fr', 'label': 'argent'},
            ], 
            'type': 'concept',
            'id': 19, 
            'related': []}
]

materials = DictionaryProvider(
    {'id': 'MATERIAL'},
    mdata,
    uri_generator = UriPatternGenerator('urn:x-vioe:materials:%s')
)
