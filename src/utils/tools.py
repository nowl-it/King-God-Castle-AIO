"""
Tools Manager
Handles the management and execution of external tools
"""

import subprocess, platform, os
from pathlib import Path


class ToolsManager:
    """Manager for external tools like apkeep and asset-ripper"""

    def __init__(self):
        self.scripts_dir = Path(os.path.join(os.getcwd(), "scripts"))

    def platform(self):
        """Detect current platform for tool selection"""
        system = platform.system().lower()
        machine = platform.machine().lower()

        if system == "linux":
            return "linux-x64" if "x86_64" in machine else "linux-arm64"
        # elif system == "darwin":
        #     return "osx-x64" if "x86_64" in machine else "osx-arm64"
        elif system == "windows":
            return "win-x64"
        else:
            return "unknown"

    def apkeep(self, args=None):
        """Get apkeep command for current platform (always from app/scripts)"""
        if args is None:
            args = []
        script_path = self.scripts_dir / (
            "apkeep.exe" if platform.system() == "Windows" else "apkeep"
        )

        return [str(script_path)] + args

    def asset_ripper(self, args=None):
        """Get asset-ripper command for current platform (always from app/scripts)"""
        if args is None:
            args = []
        script_path = self.scripts_dir / (
            "asset-ripper-win-x64/AssetRipper.GUI.Free.exe"
            if platform.system() == "Windows"
            else "asset-ripper-linux-x64/AssetRipper.GUI.Free"
        )
        return [str(script_path)] + args

    def check_tools(self):
        """Check if tools are available and working"""
        results = {}

        try:
            # Check apkeep
            cmd = self.apkeep(["--version"])
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            results["apkeep"] = result.returncode == 0
        except Exception:
            results["apkeep"] = False

        try:
            # Check asset-ripper
            cmd = self.asset_ripper(["--help"])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            results["asset-ripper"] = result.stdout != ""
        except Exception:
            results["asset-ripper"] = False

        return results


tools = ToolsManager()
