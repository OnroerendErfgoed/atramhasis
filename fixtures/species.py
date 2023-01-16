"""
Testdata cotaining species

.. versionadded:: 0.4.4
"""


from skosprovider.providers import DictionaryProvider
from skosprovider.uri import UriPatternGenerator
from .species_data import SPECIESDATA

species = DictionaryProvider(
    {'id': 'SPECIES'},
    SPECIESDATA,
    uri_generator=UriPatternGenerator('https://id.erfgoed.net/thesauri/soorten/%s')
)
