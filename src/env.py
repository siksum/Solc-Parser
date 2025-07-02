import platform
import subprocess
import sys
import argparse

def mac_can_run_intel_binaries() -> bool:
    """Check if the Mac is Intel or M1 with available Rosetta. Will throw an exception if run on non-macOS."""
    assert sys.platform == "darwin"
    if platform.machine() == "arm64":
        # M1/M2 Mac
        result = subprocess.run(["/usr/bin/pgrep", "-q", "oahd"], capture_output=True, check=False)
        return result.returncode == 0

    # Intel Mac
    return True

def halt_incompatible_system() -> None:
    if soliditylang_platform() == "macos-amd64" and not mac_can_run_intel_binaries():
        raise argparse.ArgumentTypeError(
            "solc binaries for macOS are Intel-only. Please install Rosetta on your Mac to continue. Refer to the solc-select README for instructions."
        )
    

def soliditylang_platform() -> str:
    if sys.platform.startswith("linux"):
        platform = "linux-amd64"
    elif sys.platform == "darwin":
        platform = "macosx-amd64"
    else:
        raise argparse.ArgumentTypeError("Unsupported platform")
    return platform

    
