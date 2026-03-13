#!/usr/bin/env python3
"""Check whether the current Python environment can support a tkinter + VLC player."""

from __future__ import annotations

import importlib
import json
import platform
import shutil
import sys


def check_module(name: str) -> dict:
    try:
        module = importlib.import_module(name)
    except Exception as exc:  # pragma: no cover - diagnostic script
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}

    version = getattr(module, "__version__", None)
    return {"available": True, "version": version}


def main() -> int:
    report = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "modules": {
            "tkinter": check_module("tkinter"),
            "vlc": check_module("vlc"),
        },
        "vlc_binary_in_path": shutil.which("vlc"),
    }

    print(json.dumps(report, indent=2))

    missing = [name for name, info in report["modules"].items() if not info["available"]]
    if missing:
        print(
            "\nMissing runtime pieces: "
            + ", ".join(missing)
            + ". Install the Python packages and ensure VLC is installed on the system."
        )
        return 1

    if report["vlc_binary_in_path"] is None:
        print("\nPython modules import correctly, but the VLC binary was not found in PATH.")
        return 1

    print("\nEnvironment looks ready for a basic tkinter + python-vlc desktop player.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
