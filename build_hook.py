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
                'pybabel',
                'compile',
                '--directory',
                'atramhasis/locale',
                '--domain',
                'atramhasis',
            ],
            cwd=root_dir,
            check=True,
        )

    def build_frontend(self):
        root_dir = Path(__file__).parent
        static = root_dir / 'atramhasis' / 'static'
        static_admin = static / 'admin'
        subprocess.run(['npm', 'install'], cwd=static, check=True)
        subprocess.run(['npm', 'install'], cwd=static_admin, check=True)
        subprocess.run(['grunt', '-v', 'build'], cwd=static_admin, check=True)
