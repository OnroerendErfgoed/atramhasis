"""
Testdata containing blue birds such as the famous Norwegian Blue

.. versionadded:: 2.0.0
"""


from skosprovider.providers import DictionaryProvider
from .bluebirds_data import BLUEBIRDSDATA

bluebirds = DictionaryProvider(
    {'id': 'BLUEBIRDS'},
    BLUEBIRDSDATA
)
