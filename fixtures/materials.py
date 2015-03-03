# -*- coding: utf-8 -*-
'''
Testdata cotaining materials: concrete, glass, metal, silex, ...

.. versionadded:: 0.2.0
'''

from __future__ import unicode_literals

from skosprovider.providers import DictionaryProvider
from skosprovider.uri import UriPatternGenerator
from .materiaal_data import MATERIAALDATA

materials = DictionaryProvider(
    {'id': 'MATERIAL'},
    MATERIAALDATA,
    uri_generator = UriPatternGenerator('https://id.erfgoed.net/thesauri/materialen/%s')
)
