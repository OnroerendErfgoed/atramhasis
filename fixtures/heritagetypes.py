# -*- coding: utf-8 -*-
'''
Testdata cotaining heritage types

.. versionadded:: 0.4.4
'''

from __future__ import unicode_literals

from skosprovider.providers import DictionaryProvider
from skosprovider.uri import UriPatternGenerator
from .heritagetypes_data import HERITAGETYPESDATA

heritagetypes = DictionaryProvider(
    {'id': 'HERITAGETYPE'},
    HERITAGETYPESDATA,
    uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/erfgoedtypes/%s')
)
