# -*- coding: utf-8 -*-
import optparse
import sys
import os
import time
import textwrap
from datetime import datetime

from pyramid.paster import bootstrap, setup_logging

import json

from atramhasis.errors import (
    SkosRegistryNotFoundException
)



def main():
    description = """\
    Generate a config file for a LDF server.
    """
    usage = "usage: %prog config_uri"
    parser = optparse.OptionParser(
        usage=usage,
        description=textwrap.dedent(description)
    )
    parser.add_option(
        '-l', '--location', dest='config_location', type='string',
        help='Specify where to put the config file. If not specified, this \
is set to the atramhasis.ldf.config_location from your ini file.'
    )

    options, args = parser.parse_args(sys.argv[1:])

    if not len(args) >= 1:
        print('You must provide at least one argument.')
        return 2

    config_uri = args[0]

    env = bootstrap(config_uri)
    setup_logging(config_uri)

    config_location = options.config_location
    if config_location is None:
        config_location = env['registry'].settings.get(
            'atramhasis.ldf.config_location',
            os.path.abspath(os.path.dirname(config_uri))
        )

    dump_location = env['registry'].settings.get(
        'atramhasis.dump_location',
        os.path.abspath(os.path.dirname(config_uri))
    )

    ldf_baseurl = env['registry'].settings.get(
        'atramhasis.ldf.baseurl',
        None
    )

    ldf_protocol = env['registry'].settings.get(
        'atramhasis.ldf.protocol',
        None
    )

    request = env['request']

    if hasattr(request, 'skos_registry') and request.skos_registry is not None:
        skos_registry = request.skos_registry
    else:
        raise SkosRegistryNotFoundException()   # pragma: no cover

    start_time = time.time()
    ldfconfig = {
        'title': 'Atramhasis LDF server',
        'datasources': {},
        'prefixes': {
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'owl': 'http://www.w3.org/2002/07/owl#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            'hydra': 'http://www.w3.org/ns/hydra/core#',
            'void': 'http://rdfs.org/ns/void#',
            'skos': 'http://www.w3.org/2004/02/skos/core#',
            'skos-thes': 'http://purl.org/iso25964/skos-thes#'
        }
    }

    if ldf_baseurl:
        ldfconfig['baseURL'] = ldf_baseurl

    if ldf_protocol:
        ldfconfig['protocol'] = ldf_protocol

    pids = []
    for p in skos_registry.get_providers():
        if any([not_shown in p.get_metadata()['subject'] for not_shown in ['external']]):
            continue;
        pid = p.get_metadata()['id']
        pids.append(pid)
        filename = os.path.join(dump_location, '%s-full' % pid)
        filename_ttl = filename + '.ttl'
        filename_hdt = filename + '.hdt'
        if os.path.isfile(filename_hdt):
            dumptype = 'HdtDatasource'
            dumpfile = filename_hdt
        else:
            dumptype = 'TurtleDatasource'
            dumpfile = filename_ttl
        sourceconfig = {
            'title': p.concept_scheme.label().label if p.concept_scheme.label() else pid,
            'type': dumptype,
            'settings': {
                'file': dumpfile
            }
        }
        for n in p.concept_scheme.notes:
            if n.type in ['definition', 'scopeNote']:
                sourceconfig['description'] = n.note
                break
        ldfconfig['datasources'][pid] = sourceconfig

    if len(pids):
        sourceconfig = {
            'title': 'All conceptschemes',
            'type': 'CompositeDatasource',
            'description': 'All conceptschemes contained in this Atramhasis instance together.',
            'settings': {
                'references': pids
            }
        }
        ldfconfig['datasources']['composite'] = sourceconfig


    config_filename = os.path.join(config_location, 'ldf_server_config.json')

    with open(config_filename, 'w') as fp:
        json.dump(ldfconfig, fp, indent=4)

    print('Config written to %s.' % config_filename)

    print("--- %s seconds ---" % (time.time() - start_time))

    env['closer']()
