"""
Testdata cotaining event types

.. versionadded:: 0.4.4
"""


from skosprovider.providers import DictionaryProvider
from skosprovider.uri import UriPatternGenerator
from .eventtypes_data import EVENTTYPESDATA

eventtypes = DictionaryProvider(
    {'id': 'EVENTTYPE'},
    EVENTTYPESDATA,
    uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/gebeurtenistypes/%s')
)
