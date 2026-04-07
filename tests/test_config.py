import logging
import os
import tempfile

from pyramid.paster import get_appsettings

from atramhasis import main
from atramhasis import parse_json_setting

here = os.path.dirname(__file__)
settings = get_appsettings(os.path.join(here, "../", "tests/conf_test.ini"))


class TestConfig:
    def test_config(self, db_session):
        app = main({}, **settings)
        assert app is not None

    def test_config_alt_dump_location(self, db_session):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings["atramhasis.dump_location"] = temp_dir
            app = main({}, **settings)
            assert app is not None


class TestParseJsonSetting:
    def test_valid_json(self):
        s = {"my.key": '["a", "b"]'}
        parse_json_setting(s, "my.key")
        assert s["my.key"] == ["a", "b"]

    def test_empty_string_removes_key(self):
        s = {"my.key": ""}
        parse_json_setting(s, "my.key")
        assert "my.key" not in s

    def test_whitespace_only_removes_key(self):
        s = {"my.key": "   "}
        parse_json_setting(s, "my.key")
        assert "my.key" not in s

    def test_missing_key_is_noop(self):
        s = {}
        parse_json_setting(s, "my.key")
        assert "my.key" not in s

    def test_invalid_json_removes_key_and_warns(self, caplog):
        s = {"my.key": "{bad json}"}
        with caplog.at_level(logging.WARNING):
            parse_json_setting(s, "my.key")
        assert "my.key" not in s
        assert "Invalid JSON for 'my.key'" in caplog.text
