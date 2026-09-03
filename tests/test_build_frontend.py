import json
from unittest import mock

import pytest

from scripts import build_frontend

MANIFEST = {
    "src/main.ts": {
        "file": "dist/main.abc123.js",
        "css": ["dist/main.def456.css"],
    }
}


@pytest.fixture
def project(tmp_path):
    """A minimal project tree with a Vite manifest and a placeholder template."""
    (tmp_path / "frontend").mkdir()
    manifest_dir = tmp_path / "atramhasis" / "static" / "dist" / ".vite"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "manifest.json").write_text(json.dumps(MANIFEST))
    templates = tmp_path / "atramhasis" / "templates"
    templates.mkdir(parents=True)
    (templates / "admin_placeholder.jinja2").write_text(
        "<head>\n      <!-- if production -->\n</head>\n"
    )
    return tmp_path


def test_build_frontend_installs_and_builds_in_the_frontend_dir(project):
    with mock.patch("scripts.build_frontend.subprocess.run") as run:
        build_frontend.build_frontend(project)

    assert [call.args[0] for call in run.call_args_list] == [
        ["pnpm", "install"],
        ["pnpm", "build"],
    ]
    assert all(
        call.kwargs["cwd"] == project / "frontend" for call in run.call_args_list
    )
    # The build itself must not abort the setup on a type error.
    assert run.call_args_list[0].kwargs["check"] is True
    assert run.call_args_list[1].kwargs["check"] is False


def test_build_frontend_renders_the_admin_template(project):
    with mock.patch("scripts.build_frontend.subprocess.run"):
        build_frontend.build_frontend(project)

    admin = (project / "atramhasis" / "templates" / "admin.jinja2").read_text()
    assert "<!-- if production -->" not in admin
    assert 'href="/static/dist/main.def456.css"' in admin
    assert 'src="/static/dist/main.abc123.js"' in admin
