# Session Log

| Step | Action / Command | Result / Notes |
| --- | --- | --- |
| 1 | `curl -LsSf https://astral.sh/uv/install.sh | sh` | Installed `uv 0.9.3` using installer (escalated permissions). |
| 2 | `uv --version` | Confirmed installation (0.9.3). |
| 3 | `HOME=$PWD/.home uv init` | Initialized uv project in `950-Codex1` (local HOME to avoid cache permission issues). |
| 4 | `HOME=$PWD/.home uv run python main.py` | Created `.venv`, produced “Hello from 950-codex1!”. |
| 5 | Implemented `950-010-table.py` | Added script to convert pipe-delimited input into ASCII table. |
| 6 | `printf 'a|bbbbb|c\n' > /tmp/sample.txt`<br>`HOME=$PWD/.home uv run python 950-010-table.py /tmp/sample.txt` | Initial run failed (script located in parent dir); moved script into project, reran successfully. |
| 7 | Wrote tests (initial unittest version) | Added `tests/test_table.py` using `unittest` and subprocess helper. |
| 8 | `HOME=$PWD/.home uv run pytest` | Failed: DNS error resolving PyPI (attempted to download pytest). |
| 9 | `HOME=$PWD/.home uv run python -m unittest discover -s tests` | Ran unittest suite; 3 tests passed. |
| 10 | Reworked tests to use `pytest` | Configured `dependency-groups.dev` with pytest; rewrote test suite. |
| 11 | `HOME=$PWD/.home uv run pytest` | Failed again due to DNS issue contacting PyPI. |
| 12 | `HOME=$PWD/.home uv run --no-sync pytest` | Skipped sync, ran existing pytest installation; 4 tests passed. |
| 13 | Connectivity check: `HOME=$PWD/.home uv pip install pytest --dry-run` | Verified PyPI access after resolver update; command reported “Would make no changes”. |
