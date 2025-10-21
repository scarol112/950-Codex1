#!/usr/bin/env python3
"""Compatibility wrapper for the table_tool CLI."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from table_tool.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
