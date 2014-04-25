# -*- coding: utf-8 -*-
'''
Testdata cotaining stylistic (eg. Gothic, Romanesque) and cultural periods 
(eg. La Tène)

.. versionadded:: 0.2.0
'''

from skosprovider.providers import DictionaryProvider
from skosprovider.uri import UriPatternGenerator


sdata = [
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'acheuleaan'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Acheulien'}], 'type': 'concept', 'id': 64, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'ahrensburgiaan'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Ahrensburgien'}], 'type': 'concept', 'id': 65, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'art deco'}], 'type': 'concept', 'id': 22, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'art nouveau'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Jugendstil'}], 'type': 'concept', 'id': 30, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'aurignaciaan'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Aurignacien'}], 'type': 'concept', 'id': 66, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'barok'}], 'type': 'concept', 'id': 7, 'related': []},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'beaux-artsstijl'}], 'type': 'concept', 'id': 32, 'related': [12]},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'brutalisme'}], 'type': 'concept', 'id': 28, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'classicerende barok'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Lodewijk-XIV-stijl'}], 'type': 'concept', 'id': 8, 'related': [12]},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'classicisme'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Lodewijk XVI-stijl'}], 'type': 'concept', 'id': 10, 'related': [12]},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'cottagestijl'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Normandische stijl'}], 'type': 'concept', 'id': 31, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'creswelliaan'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Creswellien'}], 'type': 'concept', 'id': 67, 'related': []},
        {'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'culturen'}], 'type': 'collection', 'id': 61, 'members': [62, 63]},
        {'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'culturen uit de metaaltijden'}], 'type': 'collection', 'id': 63, 'members': [114, 115, 116, 117, 119, 120, 121]},
        {'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'culturen uit de steentijd'}], 'type': 'collection', 'id': 62, 'members': [64, 65, 66, 67, 68, 69, 82, 87, 88, 89, 91, 93, 95, 97, 98, 100, 102, 104, 106, 108, 109, 110, 112, 113]},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'eclecticisme'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Rundbogenstil'}], 'type': 'concept', 'id': 29, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'empire'}], 'type': 'concept', 'id': 11, 'related': [33, 36]},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'enkelgrafcultuur'}, {'type': 'altLabel', 'language': u'nl', 'label': u'standvoetbekercultuur'}, {'type': 'altLabel', 'language': u'nl', 'label': u'touwbekercultuur'}], 'type': 'concept', 'id': 68, 'related': []},
        {'broader': [23], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'expo-stijl'}], 'type': 'concept', 'id': 24, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'federmesser'}, {'type': 'altLabel', 'language': u'nl', 'label': u'aziliaan'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Azilien'}, {'type': 'altLabel', 'language': u'nl', 'label': u'tjonger'}, {'type': 'altLabel', 'language': u'nl', 'label': u'tjongeriaan'}, {'type': 'altLabel', 'language': u'nl', 'label': u'tjongercultuur'}, {'type': 'altLabel', 'language': u'nl', 'label': u'tjongertraditie'}], 'type': 'concept', 'id': 69, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'gotiek'}], 'type': 'concept', 'id': 4, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'gravettiaan'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Gravettien'}, {'type': 'altLabel', 'language': u'nl', 'label': u'périgordiaan'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Périgordien'}, {'type': 'altLabel', 'language': u'nl', 'label': u'perigordiaan'}], 'type': 'concept', 'id': 82, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'groupe de Blicquy'}], 'type': 'concept', 'id': 87, 'related': []},
        {'broader': [63], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'Halstatt'}], 'type': 'concept', 'id': 114, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'hamburgiaan'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Hamburgien'}], 'type': 'concept', 'id': 88, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'hazendonkgroep'}], 'type': 'concept', 'id': 89, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'high tech'}], 'type': 'concept', 'id': 27, 'related': []},
        {'broader': [63], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'Hilversum-cultuur'}], 'type': 'concept', 'id': 115, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'klokbekercultuur'}, {'type': 'altLabel', 'language': u'nl', 'label': u'KB'}], 'type': 'concept', 'id': 91, 'related': []},
        {'broader': [63], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'La Tène'}], 'type': 'concept', 'id': 116, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'lineaire bandkeramiek'}, {'type': 'altLabel', 'language': u'nl', 'label': u'LBK'}], 'type': 'concept', 'id': 93, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'magdaleniaan'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Magdalenien'}], 'type': 'concept', 'id': 95, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'michelsbergcultuur'}], 'type': 'concept', 'id': 97, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'micoquiaan'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Micoquien'}], 'type': 'concept', 'id': 98, 'related': []},
        {'broader': [60], 'narrower': [24], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'modernisme'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Nieuwe Zakelijkheid'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Internationale Stijl'}, {'type': 'altLabel', 'language': u'nl', 'label': u'functionalisme'}, {'type': 'altLabel', 'language': u'nl', 'label': u'pakketbootstijl'}], 'type': 'concept', 'id': 23, 'related': []},
        
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'mousteriaan'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Mousterien'}], 'type': 'concept', 'id': 100, 'related': []},
        {'broader': [63], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'Nederrijnse grafheuvelcultuur'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Niederrheinische grabhügelkultur'}], 'type': 'concept', 'id': 117, 'related': []},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'neo-Egyptisch'}], 'type': 'concept', 'id': 34, 'related': []},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'neo-empire'}], 'type': 'concept', 'id': 33, 'related': [11, 36]},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'neobarok'}, {'type': 'altLabel', 'language': u'nl', 'label': u'neo-Lodewijk-XIV-stijl'}], 'type': 'concept', 'id': 16, 'related': []},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'neobyzantijns'}], 'type': 'concept', 'id': 18, 'related': []},
        {'broader': [35], 'narrower': [36], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'neoclassicisme'}, {'type': 'altLabel', 'language': u'nl', 'label': u'neo-Lodewijk XVI-stijl'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Louis-Philippestijl'}], 'type': 'concept', 'id': 12, 'related': [8, 10, 32]},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'neogotiek'}, {'type': 'altLabel', 'language': u'nl', 'label': u'neotudorstijl'}, {'type': 'altLabel', 'language': u'nl', 'label': u'troubadourstijl'}], 'type': 'concept', 'id': 13, 'related': []},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'neomoors'}], 'type': 'concept', 'id': 17, 'related': []},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'neorenaissance'}], 'type': 'concept', 'id': 14, 'related': []},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'neorococo'}, {'type': 'altLabel', 'language': u'nl', 'label': u'neo-Lodewijk-XV-stijl'}], 'type': 'concept', 'id': 19, 'related': []},
        {'broader': [35], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'neoromaans'}], 'type': 'concept', 'id': 15, 'related': []},
        {'broader': [60], 'narrower': [12, 13, 14, 15, 16, 17, 18, 19, 29, 32, 33, 34], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'neostijl'}], 'type': 'concept', 'id': 35, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'neotraditioneel'}], 'type': 'concept', 'id': 21, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'organische architectuur'}], 'type': 'concept', 'id': 25, 'related': []},
        {'broader': [63], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'Plainseaucultuur'}], 'type': 'concept', 'id': 119, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'postmodernisme'}], 'type': 'concept', 'id': 26, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'regionalisme'}], 'type': 'concept', 'id': 20, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'renaissance'}], 'type': 'concept', 'id': 5, 'related': []},
        {'broader': [63], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'Rhin-Suisse-France Oriental'}], 'type': 'concept', 'id': 120, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'Rijnbekkengroep'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Rheinbasin-kreis'}], 'type': 'concept', 'id': 102, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'rococo'}, {'type': 'altLabel', 'language': u'nl', 'label': u'régence'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Lodewijk-XV-stijl'}], 'type': 'concept', 'id': 9, 'related': []},
        {'broader': [60], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'romaans'}], 'type': 'concept', 'id': 3, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'rössencultuur'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Roessener'}], 'type': 'concept', 'id': 104, 'related': []},
        {'broader': [12], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'second empire'}], 'type': 'concept', 'id': 36, 'related': [11, 33]},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'Seine-Oise-Marne'}, {'type': 'altLabel', 'language': u'nl', 'label': u'SOM'}], 'type': 'concept', 'id': 106, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'steingroep'}], 'type': 'concept', 'id': 108, 'related': []},
        {'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'stijlen'}], 'type': 'collection', 'id': 60, 'members': [1, 3, 4, 5, 7, 8, 9, 10, 11, 20, 21, 22, 23, 25, 26, 27, 28, 30, 31, 35]},
        {'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'Stijlen en culturen'}], 'type': 'collection', 'id': 0, 'members': [60, 61]},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'swifterbantcultuur'}], 'type': 'concept', 'id': 109, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'tardenoisiaan'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Tardenoisien'}], 'type': 'concept', 'id': 110, 'related': []},
        {'broader': [60], 'narrower': [2], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'traditioneel'}, {'type': 'altLabel', 'language': u'nl', 'label': u'bak- en zandsteenstijl'}, {'type': 'altLabel', 'language': u'nl', 'label': u'Maasstijl'}], 'type': 'concept', 'id': 1, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'trechterbekercultuur'}], 'type': 'concept', 'id': 112, 'related': []},
        {'broader': [63], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'urnenveldencultuur'}], 'type': 'concept', 'id': 121, 'related': []},
        {'broader': [1], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'vakwerkbouw'}], 'type': 'concept', 'id': 2, 'related': []},
        {'broader': [62], 'narrower': [], 'notes': [], 'labels': [{'type': 'prefLabel', 'language': u'nl', 'label': u'vlaardingencultuur'}], 'type': 'concept', 'id': 113, 'related': []}
]

styles_and_cultures = DictionaryProvider(
    {'id': 'STYLE'},
    sdata,
    uri_generator = UriPatternGenerator(u'urn:x-vioe:styles:%s')
)
