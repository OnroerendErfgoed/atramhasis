import subprocess
import sys
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
        """Build the frontend.

        The actual work lives in scripts/build_frontend.py so that the wheel
        build and `mise run setup` (setup:frontend) build the frontend in the
        exact same way.
        """
        root_dir = Path(__file__).parent
        subprocess.run(
            [sys.executable, str(root_dir / "scripts" / "build_frontend.py")],
            check=True,
        )
