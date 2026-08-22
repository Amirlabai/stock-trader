"""Resolve pipeline/.venv python on Windows or Unix, then run run_screen.py."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_WIN = ROOT / ".venv" / "Scripts" / "python.exe"
VENV_UNIX = ROOT / ".venv" / "bin" / "python"


def main() -> int:
    py = VENV_WIN if VENV_WIN.exists() else VENV_UNIX
    if not py.exists():
        print(f"Missing venv python at {VENV_WIN} or {VENV_UNIX}", file=sys.stderr)
        return 1
    return subprocess.call([str(py), str(ROOT / "run_screen.py"), *sys.argv[1:]])


if __name__ == "__main__":
    raise SystemExit(main())
