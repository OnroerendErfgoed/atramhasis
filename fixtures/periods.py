"""
Testdata cotaining periods

.. versionadded:: 0.4.4
"""


from skosprovider.providers import DictionaryProvider
from skosprovider.uri import UriPatternGenerator
from .periods_data import PERIODSDATA

periods = DictionaryProvider(
    {'id': 'PERIOD'},
    PERIODSDATA,
    uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/dateringen/%s')
)
