import json
import subprocess
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class BuildHook(BuildHookInterface):
    def initialize(self, version: str, build_data) -> None:
        """Execute compilations when building the wheel."""
        super().initialize(version, build_data)

        self.build_frontend()
        self.compile_message_catalog()

    def compile_message_catalog(self):
        root_dir = Path(__file__).parent
        subprocess.run(
            [
                "pybabel",
                "compile",
                "--directory",
                "atramhasis/locale",
                "--domain",
                "atramhasis",
            ],
            cwd=root_dir,
            check=True,
        )

    def build_frontend(self):
        root_dir = Path(__file__).parent

        frontend = root_dir / "frontend"
        backend = root_dir / "atramhasis"

        subprocess.run(["pnpm", "install"], cwd=frontend, check=True)
        subprocess.run(["pnpm", "build"], cwd=frontend, check=True)

        static = backend / "static"
        static_dist = static / "dist"
        templates = backend / "templates"

        with (static_dist / ".vite" / "manifest.json").open() as manifest_file:
            manifest = json.load(manifest_file)

        vue_config = f"""
            <link
                rel="stylesheet"
                href="/static/{manifest["src/main.ts"]["css"][0]}"
                />
            <script
                type="module"
                src="/static/{manifest["src/main.ts"]["file"]}">
            </script>
        """

        contents = (templates / "admin_placeholder.jinja2").read_text()
        contents = contents.replace("<!-- if production -->", vue_config)
        (templates / "admin.jinja2").write_text(contents)
