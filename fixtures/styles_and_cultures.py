# -*- coding: utf-8 -*-
'''
Testdata cotaining stylistic (eg. Gothic, Romanesque) and cultural periods 
(eg. La Tène)

.. versionadded:: 0.2.0
'''

from __future__ import unicode_literals

from skosprovider.providers import DictionaryProvider
from skosprovider.uri import UriPatternGenerator


sdata = [
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'acheuleaan'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Acheulien'}], 'type': 'concept', 'id': 64, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'ahrensburgiaan'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Ahrensburgien'}], 'type': 'concept', 'id': 65, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'art deco'}], 'type': 'concept', 'id': 22, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'art nouveau'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Jugendstil'}], 'type': 'concept', 'id': 30, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'aurignaciaan'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Aurignacien'}], 'type': 'concept', 'id': 66, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'barok'}], 'type': 'concept', 'id': 7, 'related': []},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'beaux-artsstijl'}], 'type': 'concept', 'id': 32, 'related': [12]},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'brutalisme'}], 'type': 'concept', 'id': 28, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'classicerende barok'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Lodewijk-XIV-stijl'}], 'type': 'concept', 'id': 8, 'related': [12]},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'classicisme'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Lodewijk XVI-stijl'}], 'type': 'concept', 'id': 10, 'related': [12]},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'cottagestijl'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Normandische stijl'}], 'type': 'concept', 'id': 31, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'creswelliaan'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Creswellien'}], 'type': 'concept', 'id': 67, 'related': []},
        {'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'culturen'}], 'type': 'collection', 'id': 61, 'members': [62, 63]},
        {'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'culturen uit de metaaltijden'}], 'type': 'collection', 'id': 63, 'members': [114, 115, 116, 117, 119, 120, 121]},
        {'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'culturen uit de steentijd'}], 'type': 'collection', 'id': 62, 'members': [64, 65, 66, 67, 68, 69, 82, 87, 88, 89, 91, 93, 95, 97, 98, 100, 102, 104, 106, 108, 109, 110, 112, 113]},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'eclecticisme'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Rundbogenstil'}], 'type': 'concept', 'id': 29, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'empire'}], 'type': 'concept', 'id': 11, 'related': [33, 36]},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'enkelgrafcultuur'}, {'type': 'altLabel', 'language': 'nl', 'label': 'standvoetbekercultuur'}, {'type': 'altLabel', 'language': 'nl', 'label': 'touwbekercultuur'}], 'type': 'concept', 'id': 68, 'related': []},
        {'broader': [23], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'expo-stijl'}], 'type': 'concept', 'id': 24, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'federmesser'}, {'type': 'altLabel', 'language': 'nl', 'label': 'aziliaan'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Azilien'}, {'type': 'altLabel', 'language': 'nl', 'label': 'tjonger'}, {'type': 'altLabel', 'language': 'nl', 'label': 'tjongeriaan'}, {'type': 'altLabel', 'language': 'nl', 'label': 'tjongercultuur'}, {'type': 'altLabel', 'language': 'nl', 'label': 'tjongertraditie'}], 'type': 'concept', 'id': 69, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'gotiek'}], 'type': 'concept', 'id': 4, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'gravettiaan'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Gravettien'}, {'type': 'altLabel', 'language': 'nl', 'label': 'périgordiaan'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Périgordien'}, {'type': 'altLabel', 'language': 'nl', 'label': 'perigordiaan'}], 'type': 'concept', 'id': 82, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'groupe de Blicquy'}], 'type': 'concept', 'id': 87, 'related': []},
        {'broader': [63], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'Halstatt'}], 'type': 'concept', 'id': 114, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'hamburgiaan'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Hamburgien'}], 'type': 'concept', 'id': 88, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'hazendonkgroep'}], 'type': 'concept', 'id': 89, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'high tech'}], 'type': 'concept', 'id': 27, 'related': []},
        {'broader': [63], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'Hilversum-cultuur'}], 'type': 'concept', 'id': 115, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'klokbekercultuur'}, {'type': 'altLabel', 'language': 'nl', 'label': 'KB'}], 'type': 'concept', 'id': 91, 'related': []},
        {'broader': [63], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'La Tène'}], 'type': 'concept', 'id': 116, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'lineaire bandkeramiek'}, {'type': 'altLabel', 'language': 'nl', 'label': 'LBK'}], 'type': 'concept', 'id': 93, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'magdaleniaan'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Magdalenien'}], 'type': 'concept', 'id': 95, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'michelsbergcultuur'}], 'type': 'concept', 'id': 97, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'micoquiaan'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Micoquien'}], 'type': 'concept', 'id': 98, 'related': []},
        {'broader': [60], 'narrower': [24], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'modernisme'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Nieuwe Zakelijkheid'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Internationale Stijl'}, {'type': 'altLabel', 'language': 'nl', 'label': 'functionalisme'}, {'type': 'altLabel', 'language': 'nl', 'label': 'pakketbootstijl'}], 'type': 'concept', 'id': 23, 'related': []},
        
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'mousteriaan'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Mousterien'}], 'type': 'concept', 'id': 100, 'related': []},
        {'broader': [63], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'Nederrijnse grafheuvelcultuur'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Niederrheinische grabhügelkultur'}], 'type': 'concept', 'id': 117, 'related': []},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'neo-Egyptisch'}], 'type': 'concept', 'id': 34, 'related': []},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'neo-empire'}], 'type': 'concept', 'id': 33, 'related': [11, 36]},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'neobarok'}, {'type': 'altLabel', 'language': 'nl', 'label': 'neo-Lodewijk-XIV-stijl'}], 'type': 'concept', 'id': 16, 'related': []},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'neobyzantijns'}], 'type': 'concept', 'id': 18, 'related': []},
        {'broader': [35], 'narrower': [36], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'neoclassicisme'}, {'type': 'altLabel', 'language': 'nl', 'label': 'neo-Lodewijk XVI-stijl'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Louis-Philippestijl'}], 'type': 'concept', 'id': 12, 'related': [8, 10, 32]},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'neogotiek'}, {'type': 'altLabel', 'language': 'nl', 'label': 'neotudorstijl'}, {'type': 'altLabel', 'language': 'nl', 'label': 'troubadourstijl'}], 'type': 'concept', 'id': 13, 'related': []},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'neomoors'}], 'type': 'concept', 'id': 17, 'related': []},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'neorenaissance'}], 'type': 'concept', 'id': 14, 'related': []},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'neorococo'}, {'type': 'altLabel', 'language': 'nl', 'label': 'neo-Lodewijk-XV-stijl'}], 'type': 'concept', 'id': 19, 'related': []},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'neoromaans'}], 'type': 'concept', 'id': 15, 'related': []},
        {'broader': [60], 'narrower': [12, 13, 14, 15, 16, 17, 18, 19, 29, 32, 33, 34], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'neostijl'}], 'type': 'concept', 'id': 35, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'neotraditioneel'}], 'type': 'concept', 'id': 21, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'organische architectuur'}], 'type': 'concept', 'id': 25, 'related': []},
        {'broader': [63], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'Plainseaucultuur'}], 'type': 'concept', 'id': 119, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'postmodernisme'}], 'type': 'concept', 'id': 26, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'regionalisme'}], 'type': 'concept', 'id': 20, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'renaissance'}], 'type': 'concept', 'id': 5, 'related': []},
        {'broader': [63], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'Rhin-Suisse-France Oriental'}], 'type': 'concept', 'id': 120, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'Rijnbekkengroep'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Rheinbasin-kreis'}], 'type': 'concept', 'id': 102, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'rococo'}, {'type': 'altLabel', 'language': 'nl', 'label': 'régence'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Lodewijk-XV-stijl'}], 'type': 'concept', 'id': 9, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'romaans'}], 'type': 'concept', 'id': 3, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'rössencultuur'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Roessener'}], 'type': 'concept', 'id': 104, 'related': []},
        {'broader': [12], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'second empire'}], 'type': 'concept', 'id': 36, 'related': [11, 33]},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'Seine-Oise-Marne'}, {'type': 'altLabel', 'language': 'nl', 'label': 'SOM'}], 'type': 'concept', 'id': 106, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'steingroep'}], 'type': 'concept', 'id': 108, 'related': []},
        {'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'stijlen'}], 'type': 'collection', 'id': 60, 'members': [1, 3, 4, 5, 7, 8, 9, 10, 11, 20, 21, 22, 23, 25, 26, 27, 28, 30, 31, 35]},
        {'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'Stijlen en culturen'}], 'type': 'collection', 'id': 0, 'members': [60, 61]},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'swifterbantcultuur'}], 'type': 'concept', 'id': 109, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'tardenoisiaan'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Tardenoisien'}], 'type': 'concept', 'id': 110, 'related': []},
        {'broader': [60], 'narrower': [2], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'traditioneel'}, {'type': 'altLabel', 'language': 'nl', 'label': 'bak- en zandsteenstijl'}, {'type': 'altLabel', 'language': 'nl', 'label': 'Maasstijl'}], 'type': 'concept', 'id': 1, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'trechterbekercultuur'}], 'type': 'concept', 'id': 112, 'related': []},
        {'broader': [63], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'urnenveldencultuur'}], 'type': 'concept', 'id': 121, 'related': []},
        {'broader': [1], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'vakwerkbouw'}], 'type': 'concept', 'id': 2, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': 'nl', 'label': 'vlaardingencultuur'}], 'type': 'concept', 'id': 113, 'related': []}
]

styles_and_cultures = DictionaryProvider(
    {'id': 'STYLE'},
    sdata,
    uri_generator = UriPatternGenerator('urn:x-vioe:styles:%s')
)
