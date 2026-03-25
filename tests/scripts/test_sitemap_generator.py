import os
import tempfile
import xml.etree.ElementTree as ElementTree

from atramhasis.scripts import sitemap_generator


class TestWriteElementToXml:
    def test_write_element(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            element = ElementTree.Element("urlset")
            url = ElementTree.SubElement(element, "url")
            ElementTree.SubElement(url, "loc").text = "http://example.com"
            sitemap_generator.write_element_to_xml("test.xml", tmpdir, element)
            file_path = os.path.join(tmpdir, "test.xml")
            assert os.path.isfile(file_path)
            tree = ElementTree.parse(file_path)
            root = tree.getroot()
            assert root.tag == "urlset"
            assert root.find("url/loc").text == "http://example.com"


class TestCreateDeelSitemaps:
    def test_single_part(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            urls = [f"http://example.com/{i}" for i in range(3)]
            sitemap_generator.create_deel_sitemaps(urls, 50000, tmpdir, "test")
            files = os.listdir(tmpdir)
            assert len(files) == 1
            assert "test_sitemap_deel_1.xml" in files
            tree = ElementTree.parse(os.path.join(tmpdir, files[0]))
            root = tree.getroot()
            ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            url_elements = root.findall("s:url", ns)
            assert len(url_elements) == 3

    def test_multiple_parts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            urls = [f"http://example.com/{i}" for i in range(5)]
            sitemap_generator.create_deel_sitemaps(urls, 2, tmpdir, "concepts")
            files = sorted(os.listdir(tmpdir))
            assert len(files) == 3
            assert "concepts_sitemap_deel_1.xml" in files
            assert "concepts_sitemap_deel_2.xml" in files
            assert "concepts_sitemap_deel_3.xml" in files

    def test_empty_urls(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            sitemap_generator.create_deel_sitemaps([], 50000, tmpdir, "empty")
            assert len(os.listdir(tmpdir)) == 0

    def test_exact_limit(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            urls = [f"http://example.com/{i}" for i in range(4)]
            sitemap_generator.create_deel_sitemaps(urls, 2, tmpdir, "exact")
            files = sorted(os.listdir(tmpdir))
            assert len(files) == 2


class TestCreateIndexSitemap:
    def test_creates_index(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some deel sitemaps first
            for name in [
                "concepts_sitemap_deel_1.xml",
                "concepts_sitemap_deel_2.xml",
            ]:
                element = ElementTree.Element("urlset")
                tree = ElementTree.ElementTree(element)
                tree.write(os.path.join(tmpdir, name))

            sitemap_generator.create_index_sitemap("http://example.com", tmpdir)

            index_path = os.path.join(tmpdir, "sitemap_index.xml")
            assert os.path.isfile(index_path)
            tree = ElementTree.parse(index_path)
            root = tree.getroot()
            ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            sitemaps = root.findall("s:sitemap", ns)
            assert len(sitemaps) == 2
            locs = [s.find("s:loc", ns).text for s in sitemaps]
            assert any("concepts_sitemap_deel_1.xml" in loc for loc in locs)
            assert any("concepts_sitemap_deel_2.xml" in loc for loc in locs)

    def test_excludes_index_from_listing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a sitemap and an existing index
            for name in ["test_sitemap_deel_1.xml", "sitemap_index.xml"]:
                element = ElementTree.Element("urlset")
                tree = ElementTree.ElementTree(element)
                tree.write(os.path.join(tmpdir, name))

            sitemap_generator.create_index_sitemap("http://example.com", tmpdir)

            tree = ElementTree.parse(os.path.join(tmpdir, "sitemap_index.xml"))
            root = tree.getroot()
            ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            sitemaps = root.findall("s:sitemap", ns)
            # Only the deel sitemap should be included, not the index itself
            assert len(sitemaps) == 1


class TestCreateSitemaps:
    def test_create_sitemaps_with_providers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_provider = _MockProvider(
                metadata={"id": "TREES", "subject": []},
                concepts=[{"id": "1"}, {"id": "2"}],
            )
            mock_external = _MockProvider(
                metadata={"id": "EXT", "subject": ["external"]},
                concepts=[{"id": "99"}],
            )
            mock_registry = _MockRegistry([mock_provider, mock_external])
            mock_request = type("Request", (), {"skos_registry": mock_registry})()
            env = {"request": mock_request}
            settings = {"atramhasis.url": "http://example.com"}

            sitemap_generator.create_sitemaps(settings, 50000, tmpdir, env)

            files = os.listdir(tmpdir)
            assert "sitemap_index.xml" in files
            assert any("conceptschemes_sitemap" in f for f in files)
            assert any("concepts_sitemap" in f for f in files)

    def test_external_providers_excluded(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_external = _MockProvider(
                metadata={"id": "EXT", "subject": ["external"]},
                concepts=[{"id": "1"}],
            )
            mock_registry = _MockRegistry([mock_external])
            mock_request = type("Request", (), {"skos_registry": mock_registry})()
            env = {"request": mock_request}
            settings = {"atramhasis.url": "http://example.com"}

            sitemap_generator.create_sitemaps(settings, 50000, tmpdir, env)

            files = os.listdir(tmpdir)
            # Only index should exist, no deel sitemaps for concepts
            assert "sitemap_index.xml" in files

    def test_hidden_providers_excluded(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_hidden = _MockProvider(
                metadata={"id": "HID", "subject": ["hidden"]},
                concepts=[{"id": "1"}],
            )
            mock_registry = _MockRegistry([mock_hidden])
            mock_request = type("Request", (), {"skos_registry": mock_registry})()
            env = {"request": mock_request}
            settings = {"atramhasis.url": "http://example.com"}

            sitemap_generator.create_sitemaps(settings, 50000, tmpdir, env)

            files = os.listdir(tmpdir)
            assert "sitemap_index.xml" in files


class _MockProvider:
    def __init__(self, metadata, concepts):
        self._metadata = metadata
        self._concepts = concepts

    def get_metadata(self):
        return self._metadata

    def get_all(self):
        return self._concepts


class _MockRegistry:
    def __init__(self, providers):
        self._providers = providers

    def get_providers(self):
        return self._providers
