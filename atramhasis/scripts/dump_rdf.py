# -*- coding: utf-8 -*-
import optparse
import sys
import os
import time
import textwrap

from pyramid.paster import bootstrap

from atramhasis.errors import (
    SkosRegistryNotFoundException
)

from skosprovider_rdf import utils

def main():
    description = """\
    Dump all conceptschemes to files. Will serialise as Turtle and RDF/XML format.
    """
    usage = "usage: %prog config_uri"
    parser = optparse.OptionParser(
        usage=usage,
        description=textwrap.dedent(description)
    )
    parser.add_option(
        '-l', '--location', dest='dump_location', type='string',
        help='Specify where to dump the conceptschemes. If not specified, this \
        is set to the atramhasis.dump_location from your ini file.'
    )

    options, args = parser.parse_args(sys.argv[1:])

    if not len(args) >= 1:
        print('You must provide at least one argument.')
        return 2

    config_uri = args[0]

    env = bootstrap(config_uri)

    dump_location = options.dump_location
    if dump_location is None:
        dump_location = env['registry'].settings.get(
            'atramhasis.dump_location',
            os.path.abspath(os.path.dirname(config_uri))
        )

    request = env['request']

    if hasattr(request, 'skos_registry') and request.skos_registry is not None:
        skos_registry = request.skos_registry
    else:
        raise SkosRegistryNotFoundException()   # pragma: no cover

    conceptschemes = [
        {'id': x.get_metadata()['id'],
            'conceptscheme': x.concept_scheme}
        for x in skos_registry.get_providers() if not any([not_shown in x.get_metadata()['subject']
                                                                for not_shown in ['external', 'hidden']])
    ]

    for p in skos_registry.get_providers():
        if any([not_shown in p.get_metadata()['subject'] for not_shown in ['external', 'hidden']]):
            continue;
        start_time = time.time()
        pid = p.get_metadata()['id']
        filename = os.path.join(dump_location, '%s-full' % pid)
        filename_ttl = '%s.ttl' % filename
        filename_rdf = '%s.rdf' % filename
        print('Generating dump for %s' % pid)
        graph = utils.rdf_dumper(p)
        print('Dumping %s to Turtle: %s' % (pid, filename_ttl))
        graph.serialize(destination=filename_ttl, format='turtle')
        print('Dumping %s to RDFxml: %s' % (pid, filename_rdf))
        graph.serialize(destination=filename_rdf, format='pretty-xml')
        print("--- %s seconds ---" % (time.time() - start_time))

    print('All files dumped to %s' % dump_location)

    env['closer']()
