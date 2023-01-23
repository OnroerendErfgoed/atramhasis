import logging
import optparse
import os
import sys
import textwrap
import time

import transaction
from pyramid.paster import bootstrap
from pyramid.paster import setup_logging
from rdflib import RDF
from rdflib import SKOS
from rdflib.term import URIRef
from skosprovider_rdf import utils

from atramhasis.data.datamanagers import CountsManager
from atramhasis.data.models import ConceptschemeCounts
from atramhasis.errors import SkosRegistryNotFoundException

log = logging.getLogger(__name__)


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
    parser.add_option(
        '-r', '--rdf2hdt', dest='rdf2hdt', type='string', default=False,
        help='Specify where the rdf2hdt command can be found. If not specified, this \
        is set to atramhasis.rdf2hdt from your ini file.'
    )

    options, args = parser.parse_args(sys.argv[1:])

    if not len(args) >= 1:
        log.error('You must provide at least one argument.')
        return 2

    config_uri = args[0]

    env = bootstrap(config_uri)
    setup_logging(config_uri)

    dump_location = options.dump_location
    if dump_location is None:
        dump_location = env['registry'].settings.get(
            'atramhasis.dump_location',
            os.path.abspath(os.path.dirname(config_uri))
        )
    if not os.access(dump_location, os.W_OK | os.X_OK):
        log.error('Dump location "' + dump_location + '" is not writable.')
        return 2

    rdf2hdt = options.rdf2hdt
    if not rdf2hdt:
        rdf2hdt = env['registry'].settings.get(
            'atramhasis.rdf2hdt',
            False
        )

    request = env['request']

    if hasattr(request, 'skos_registry') and request.skos_registry is not None:
        skos_registry = request.skos_registry
    else:
        raise SkosRegistryNotFoundException()  # pragma: no cover

    counts = []

    files = []

    for p in skos_registry.get_providers():
        if any([not_shown in p.get_metadata()['subject'] for not_shown in ['external']]):
            continue
        start_time = time.time()
        pid = p.get_metadata()['id']
        filename = os.path.join(dump_location, '%s-full' % pid)
        filename_ttl = '%s.ttl' % filename
        filename_rdf = '%s.rdf' % filename
        files.append(filename_ttl)
        log.info('Generating dump for %s' % pid)
        graph = utils.rdf_dumper(p)
        triples = len(graph)
        log.info('Number of triples in Graph: %d' % triples)
        csuri = URIRef(p.concept_scheme.uri)
        cs_triples = len(list(graph.predicate_objects(csuri)))
        log.info('Number of triples in Conceptscheme: %d' % cs_triples)
        count_concepts = len(list(graph.subjects(RDF.type, SKOS.Concept)))
        count_collections = len(list(graph.subjects(RDF.type, SKOS.Collection)))
        try:
            avg_concept_triples = ((triples - cs_triples) /
                                   (count_concepts + count_collections))
        except ZeroDivisionError:
            avg_concept_triples = 0
        log.info('Average number of triples per concept: %d' % avg_concept_triples)
        counts.append({
            'conceptscheme_id': pid,
            'triples': triples,
            'conceptscheme_triples': cs_triples,
            'avg_concept_triples': avg_concept_triples
        })
        log.info(f'Dumping {pid} to Turtle: {filename_ttl}')
        graph.serialize(destination=filename_ttl, format='turtle')
        log.info(f'Dumping {pid} to RDFxml: {filename_rdf}')
        graph.serialize(destination=filename_rdf, format='pretty-xml')
        del graph
        log.info(f'--- {(time.time() - start_time)} seconds ---')

    log.info('All files dumped to %s' % dump_location)

    if rdf2hdt:
        from subprocess import check_call, CalledProcessError
        parsing_error = False
        for f in files:
            log.info(f'Converting {f} to hdt')
            hdtf = f.replace('.ttl', '.hdt')
            try:
                check_call([rdf2hdt, '-f', 'turtle', f, hdtf])
            except (FileNotFoundError, CalledProcessError) as e:
                # Turtle failed, let's try rdfxml
                parsing_error = True
                log.warning(f'rdf2hdt for file {f} failed with error {e}. Trying rdfxml...')
                rdff = f.replace('.ttl', '.rdf')
                try:
                    check_call([rdf2hdt, '-f', 'rdfxml', rdff, hdtf])
                except (FileNotFoundError, CalledProcessError) as e:
                    # rdfxml failed
                    log.error(f'rdfxml for file {f} failed with error {e}')
        if parsing_error:
            log.error('Error during rdf2hdt conversion. Check logs for more information.')
        else:
            log.info(f'All hdt files dumped to {dump_location}')

    with transaction.manager:
        dbsession = request.registry.dbmaker()
        manager = CountsManager(dbsession)
        for c in counts:
            cs_count = ConceptschemeCounts(
                conceptscheme_id=c['conceptscheme_id'],
                triples=c['triples'],
                conceptscheme_triples=c['conceptscheme_triples'],
                avg_concept_triples=c['avg_concept_triples']
            )
            manager.save(cs_count)

    env['closer']()
