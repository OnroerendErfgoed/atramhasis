# -*- coding: utf-8 -*-
'''
This script helps in dumping current OE vocabularies to the fixtures folder.

Some manual post-processing is currently still needed.
'''

from skosprovider_oe.providers import (
    OnroerendErfgoedProvider
)

from skosprovider.utils import dict_dumper
import pprint
pp = pprint.PrettyPrinter(indent=4)

materiaal = OnroerendErfgoedProvider(
    {'id': 'MATERIAAL'},
    url='https://inventaris.onroerenderfgoed.be/thesaurus/materiaal'
)

stijl = OnroerendErfgoedProvider(
    {'id': 'STIJL'},
    url='https://inventaris.onroerenderfgoed.be/thesaurus/stijl'
)

pp.pprint (dict_dumper(materiaal))
