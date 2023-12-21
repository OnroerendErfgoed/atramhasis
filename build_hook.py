import subprocess
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class BuildHook(BuildHookInterface):
    def initialize(self, version: str, build_data) -> None:
        """Build frontend when building the wheel."""
        super().initialize(version, build_data)

        root_dir = Path(__file__).parent
        static = root_dir / "atramhasis" / "static"
        static_admin = static / "admin"
        subprocess.run(["npm", "install"], cwd=static)
        subprocess.run(["npm", "install"], cwd=static_admin)
        subprocess.run(["grunt", "-v", "build"], cwd=static_admin, check=True)
