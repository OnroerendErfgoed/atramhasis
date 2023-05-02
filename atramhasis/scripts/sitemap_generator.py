import argparse
import datetime
import logging
import os
import xml.etree.ElementTree as ElementTree
from builtins import input
from os import listdir
from os.path import isfile

from pyramid.paster import bootstrap
from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging

from atramhasis.errors import SkosRegistryNotFoundException

log = logging.getLogger(__name__)


def write_element_to_xml(filename, sitemap_dir, element):
    tree = ElementTree.ElementTree(element)
    file_path_name = os.path.join(sitemap_dir, filename)
    tree.write(file_path_name, encoding='utf-8', xml_declaration=True)


def create_sitemaps(settings, limit_per_deel, directory, env):
    base_url = settings.get("atramhasis.url")
    schemes_url = f"{base_url}/conceptschemes/{{}}"
    concepts_url = f"{schemes_url}/c/{{}}"

    request = env['request']

    if hasattr(request, 'skos_registry') and request.skos_registry is not None:
        skos_registry = request.skos_registry
    else:
        raise SkosRegistryNotFoundException()  # pragma: no cover

    scheme_urls = list()
    concept_urls = list()
    for p in skos_registry.get_providers():
        if any([not_shown in p.get_metadata()['subject']
                for not_shown in ['external', 'hidden']]):
            continue
        scheme_id = p.get_metadata()['id']
        scheme_urls.append(schemes_url.format(scheme_id))
        concept_urls.extend([concepts_url.format(scheme_id, x['id'])
                             for x in p.get_all()])

    create_deel_sitemaps(scheme_urls, limit_per_deel, directory, 'conceptschemes')
    create_deel_sitemaps(concept_urls, limit_per_deel, directory, 'concepts')

    create_index_sitemap(base_url, directory)


def create_deel_sitemaps(objecturls, limit_per_deel, sitemap_dir, name):
    """
    Sitemaps have a maximum amount of items. This method creates partial
    sitemaps with up to `limit_per_deel` items per file.
    """
    log.info("Beginning creation of sitemaps...")
    urlset = ElementTree.Element(
        "urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
    )
    sitemap_counter = 1

    for counter, objecturl in enumerate(objecturls, 1):
        url = ElementTree.SubElement(urlset, "url")
        ElementTree.SubElement(url, "loc").text = objecturl

        if counter % limit_per_deel == 0:
            filename = f'{name}_sitemap_deel_{sitemap_counter}.xml'
            log.info("Processed %s conceptschemes, writing %s", counter, filename)
            write_element_to_xml(filename, sitemap_dir, urlset)
            sitemap_counter += 1
            urlset = ElementTree.Element(
                "urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
            )
    if len(urlset):
        filename = f'{name}_sitemap_deel_{sitemap_counter}.xml'
        write_element_to_xml(filename, sitemap_dir, urlset)
    log.info(f"All {name} sitemaps created.")


def create_index_sitemap(base_url, directory):
    """Loop over all the created sitemaps, and create an index file."""
    log.info("Beginning creation of the final sitemap index...")
    list_sitemaps = [
        f for f in listdir(directory)
        if isfile(os.path.join(directory, f))
        and "sitemap" in f and "sitemap_index.xml" not in f
    ]
    sitemapindex = ElementTree.Element(
        "sitemapindex", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
    )
    today = datetime.date.today().isoformat()

    for file_name in list_sitemaps:
        sitemap_static_url = f"{base_url}/sitemaps/{file_name}"
        sitemap_area = ElementTree.SubElement(sitemapindex, "sitemap")
        ElementTree.SubElement(sitemap_area, "loc").text = sitemap_static_url
        ElementTree.SubElement(sitemap_area, "lastmod").text = today

    write_element_to_xml("sitemap_index.xml", directory, sitemapindex)
    log.info("Sitemap index created.")


def main():
    parser = argparse.ArgumentParser(
        description="Process some command line arguments. ",
        usage="sitemap_generator development.ini#atramhasis "
              "--limit=1000")
    parser.add_argument('settings_file',
                        help="<The location of the settings file>")
    parser.add_argument("--limit", type=int,
                        help="range of objects in sitemap", default=50000)
    parser.add_argument("--no-input", action='store_true',
                        help="Don't stop script for user input")
    args, _ = parser.parse_known_args()

    config_uri = args.settings_file
    limit = args.limit
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    env = bootstrap(config_uri)
    here = os.path.dirname(__file__)
    sitemap_dir = os.path.join(here, "..", "static", "_sitemaps")
    if os.listdir(sitemap_dir):
        print(
            "[WARNING]The target sitemap directory ({}) is not empty.\n"
            "Existing sitemaps may get overridden. But the sitemap index file "
            "will contain all sitemaps in the folder, even old ones that are "
            "no longer needed. Consider deleting the contents of the folder "
            "first.".format(os.path.abspath(sitemap_dir))
        )
        if not args.no_input:
            input("Press [Enter] to continue.")

    create_sitemaps(settings, limit, sitemap_dir, env)


if __name__ == '__main__':  # pragma: no cover
    main()
