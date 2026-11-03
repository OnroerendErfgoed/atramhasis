#!/usr/bin/env python
"""Build the Atramhasis frontend and wire it into the admin template.

Installs the frontend dependencies, builds the Vue app with Vite and then
regenerates ``atramhasis/templates/admin.jinja2`` from
``admin_placeholder.jinja2`` using the hashed asset paths from the Vite
manifest.

Shared by ``build_hook.py`` (wheel build) and ``mise run setup``
(setup:frontend), so local development and the wheel build produce the exact
same frontend.
"""

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def build_frontend(root_dir=ROOT):
    """Install the frontend dependencies, build them and render admin.jinja2."""
    root_dir = Path(root_dir)
    frontend = root_dir / "frontend"
    backend = root_dir / "atramhasis"

    subprocess.run(["pnpm", "install"], cwd=frontend, check=True)
    # `pnpm build` runs the type-check and the build in parallel with
    # --continue-on-error, so a type error must not abort the asset build.
    subprocess.run(["pnpm", "build"], cwd=frontend, check=False)

    static_dist = backend / "static" / "dist"
    templates = backend / "templates"

    with (static_dist / ".vite" / "manifest.json").open() as manifest_file:
        manifest = json.load(manifest_file)

    entry = manifest["src/main.ts"]
    vue_config = f"""
            <link
                rel="stylesheet"
                href="/static/{entry["css"][0]}"
                />
            <script
                type="module"
                src="/static/{entry["file"]}">
            </script>
        """

    contents = (templates / "admin_placeholder.jinja2").read_text()
    contents = contents.replace("<!-- if production -->", vue_config)
    (templates / "admin.jinja2").write_text(contents)


if __name__ == "__main__":
    build_frontend()
