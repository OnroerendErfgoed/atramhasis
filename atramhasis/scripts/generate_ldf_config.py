import json
import logging
import optparse
import os
import sys
import textwrap
import time

from pyramid.paster import bootstrap
from pyramid.paster import setup_logging

from atramhasis.errors import SkosRegistryNotFoundException

log = logging.getLogger(__name__)


def main():
    description = """\
    Generate a config file for a LDF server.
    """
    usage = "usage: %prog config_uri"
    parser = optparse.OptionParser(usage=usage, description=textwrap.dedent(description))
    parser.add_option(
        "-l",
        "--location",
        dest="config_location",
        type="string",
        help=(
            "Specify where to put the config file. If not specified, this is set to the"
            " atramhasis.ldf.config_location from your ini file."
        ),
    )

    options, args = parser.parse_args(sys.argv[1:])

    if not len(args) >= 1:
        log.error("You must provide at least one argument.")
        return 2

    config_uri = args[0]

    env = bootstrap(config_uri)
    setup_logging(config_uri)

    config_location = options.config_location
    if config_location is None:
        config_location = env["registry"].settings.get(
            "atramhasis.ldf.config_location", os.path.abspath(os.path.dirname(config_uri))
        )

    dump_location = env["registry"].settings.get(
        "atramhasis.dump_location", os.path.abspath(os.path.dirname(config_uri))
    )

    ldf_baseurl = env["registry"].settings.get("atramhasis.ldf.baseurl", None)

    ldf_protocol = env["registry"].settings.get("atramhasis.ldf.protocol", None)

    request = env["request"]

    if hasattr(request, "skos_registry") and request.skos_registry is not None:
        skos_registry = request.skos_registry
    else:
        raise SkosRegistryNotFoundException()  # pragma: no cover

    start_time = time.time()
    ldfconfig = {
        "@context": "https://linkedsoftwaredependencies.org/bundles/npm/@ldf/server/^3.0.0/components/context.jsonld",
        "@id": "urn:ldf-server:my",
        "import": "preset-qpf:config-defaults.json",
        "title": "Atramhasis LDF server",
        "datasources": [],
        "prefixes": [
            {"prefix": "rdf", "uri": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"},
            {"prefix": "rdfs", "uri": "http://www.w3.org/2000/01/rdf-schema#"},
            {"prefix": "owl", "uri": "http://www.w3.org/2002/07/owl#"},
            {"prefix": "xsd", "uri": "http://www.w3.org/2001/XMLSchema#"},
            {"prefix": "hydra", "uri": "http://www.w3.org/ns/hydra/core#"},
            {"prefix": "void", "uri": "http://rdfs.org/ns/void#"},
            {"prefix": "skos", "uri": "http://www.w3.org/2004/02/skos/core#"},
            {"prefix": "skos-thes", "uri": "http://purl.org/iso25964/skos-thes#"},
        ],
    }

    if ldf_baseurl:
        ldfconfig["baseURL"] = ldf_baseurl

    if ldf_protocol:
        ldfconfig["protocol"] = ldf_protocol

    pids = []
    for p in skos_registry.get_providers():
        if any([not_shown in p.get_metadata()['subject'] for not_shown in ['external']]):
            continue
        pid = p.get_metadata()["id"]
        title = p.concept_scheme.label().label if p.concept_scheme.label() else pid
        pids.append(pid)
        filename = os.path.join(dump_location, "%s-full" % pid)
        dumptype = "HdtDatasource"
        filetype = "hdtFile"
        dumpfile = filename + ".hdt"

        if not os.path.isfile(dumpfile):
            dumptype = "TurtleDatasource"
            filetype = "file"
            dumpfile = filename + ".ttl"

        sourceconfig = {
            "@id": f"urn:ldf-server:myDatasource{pid}",
            "@type": dumptype,
            "quads": False,  # TODO
            "datasourcePath": pid,
            "datasourceTitle": title,
            filetype: dumpfile,
        }

        for n in p.concept_scheme.notes:
            if n.type in ["definition", "scopeNote"]:
                sourceconfig["description"] = n.note
                break

        ldfconfig["datasources"].append(sourceconfig)

    if len(pids):
        composite_sourceconfig = {
            "@id": "urn:ldf-server:myDatasourcecomposite",
            "@type": "CompositeDatasource",
            "quads": False,  # TODO
            "datasourcePath": "composite",
            "datasourceTitle": "All conceptschemes",
            "description": (
                "All conceptschemes contained in this Atramhasis instance together."
            ),
            "compose": [f"urn:ldf-server:myDatasource{pid}" for pid in pids],
        }
        ldfconfig["datasources"].append(composite_sourceconfig)

    config_filename = os.path.join(config_location, "ldf_server_config.json")

    with open(config_filename, "w") as fp:
        json.dump(ldfconfig, fp, indent=4)

    log.info(f'Config written to {config_filename}.')

    log.info(f'--- {(time.time() - start_time)} seconds ---;')

    env["closer"]()
