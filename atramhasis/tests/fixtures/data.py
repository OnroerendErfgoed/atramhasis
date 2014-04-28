# -*- coding: utf-8 -*-
'''
Testdata cotaining two very simple conceptschemes: trees and a few geographic concepts.

.. versionadded:: 0.1.0
'''

from __future__ import unicode_literals

from skosprovider.providers import DictionaryProvider

larch = {
    'id': '1',
    'uri': 'urn:x-skosprovider:trees/1',
    'labels': [
        {'type': 'prefLabel', 'language': 'en', 'label': 'The Larch'},
        {'type': 'prefLabel', 'language': 'nl', 'label': 'De Lariks'}
    ],
    'notes': [
        {'type': 'definition', 'language': 'en', 'note': 'A type of tree.'}
    ]
}

chestnut = {
    'id': '2',
    'uri': 'urn:x-skosprovider:trees/2',
    'labels': [
        {'type': 'prefLabel', 'language': 'en', 'label': 'The Chestnut'},
        {'type': 'altLabel', 'language': 'nl', 'label': 'De Paardekastanje'},
        {'type': 'altLabel', 'language': 'fr', 'label': 'la châtaigne'},
    ],
    'notes': [
        {
            'type': 'definition', 'language': 'en',
            'note': 'A different type of tree.'
        }
    ]
}

species = {
    'id': 3,
    'uri': 'urn:x-skosprovider:trees/3',
    'labels': [
        {'type': 'prefLabel', 'language': 'en', 'label': 'Trees by species'},
        {'type': 'prefLabel', 'language': 'nl', 'label': 'Bomen per soort'}
    ],
    'type': 'collection',
    'members': ['1', '2']
}

trees = DictionaryProvider(
    {'id': 'TREES', 'default_language': 'nl'},
    [larch, chestnut, species]
)

world = {
    'id': '1',
    'labels': [
        {'type': 'prefLabel', 'language': 'en', 'label': 'World'}
    ],
    'narrower': [2, 3]
}

geo = DictionaryProvider(
    {'id': 'GEOGRAPHY'},
    [
        world,
        {
            'id': 2,
            'labels': [
                {'type': 'prefLabel', 'language': 'en', 'label': 'Europe'}
            ],
            'narrower': [4, 5], 'broader': [1]
        }, {
            'id': 3,
            'labels': [
                {
                    'type': 'prefLabel', 'language': 'en',
                    'label': 'North-America'
                }
            ],
            'narrower': [6], 'broader': [1]
        }, {
            'id': 4,
            'labels': [
                {'type': 'prefLabel', 'language': 'en', 'label': 'Belgium'}
            ],
            'narrower': [7, 8, 9], 'broader': [2]
        }, {
            'id': 5,
            'labels': [
                {
                    'type': 'prefLabel', 'language': 'en',
                    'label': 'United Kingdom'
                }
            ],
            'broader': [2]
        }, {
            'id': 6,
            'labels': [
                {
                    'type': 'prefLabel', 'language': 'en',
                    'label': 'United States of America'
                }
            ],
            'broader': [3]
        }, {
            'id': 7,
            'labels': [
                {'type': 'prefLabel', 'language': 'en', 'label': 'Flanders'}
            ],
            'broader': [4]
        }, {
            'id': 8,
            'labels': [
                {'type': 'prefLabel', 'language': 'en', 'label': 'Brussels'}
            ],
            'broader': [4]
        }, {
            'id': 9,
            'labels': [
                {'type': 'prefLabel', 'language': 'en', 'label': 'Wallonie'}
            ],
            'broader': [4]
        }, {
            'id': '333',
            'type': 'collection',
            'labels': [
                {
                    'type': 'prefLabel', 'language': 'en',
                    'label': 'Places where dutch is spoken'
                }
            ],
            'members': ['4', '7', '8']
        }
    ]
)
