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

typologie = OnroerendErfgoedProvider(
    {'id': 'HERITAGETYPE'},
    url='https://inventaris.onroerenderfgoed.be/thesaurus/typologie',
)

# with open('heritagetypes_data.py', 'w') as f:
#     f.write("""# -*- coding: utf-8 -*-
#
# HERITAGETYPESDATA= """)
#     pp = pprint.PrettyPrinter(indent=4, stream=f)
#     pp.pprint(dict_dumper(typologie))

datering = OnroerendErfgoedProvider(
    {'id': 'PERIOD'},
    url='https://inventaris.onroerenderfgoed.be/thesaurus/datering'
)

# with open('periods_data.py', 'w') as f:
#     f.write("""# -*- coding: utf-8 -*-
#
# PERIODSDATA = """)
#     pp = pprint.PrettyPrinter(indent=4, stream=f)
#     pp.pprint(dict_dumper(datering))

soort = OnroerendErfgoedProvider(
    {'id': 'SPECIES'},
    url='https://inventaris.onroerenderfgoed.be/thesaurus/soort'
)

# with open('species_data.py', 'w') as f:
#     f.write("""# -*- coding: utf-8 -*-
#
# SPECIESDATA = """)
#     pp = pprint.PrettyPrinter(indent=4, stream=f)
#     pp.pprint(dict_dumper(soort))

gebeurtenis = OnroerendErfgoedProvider(
    {'id': 'EVENTTYPE'},
    url='https://inventaris.onroerenderfgoed.be/thesaurus/gebeurtenis'
)

# with open('eventtypes_data.py', 'w') as f:
#     f.write("""# -*- coding: utf-8 -*-
#
# EVENTTYPESDATA = """)
#     pp = pprint.PrettyPrinter(indent=4, stream=f)
#     pp.pprint(dict_dumper(gebeurtenis))
