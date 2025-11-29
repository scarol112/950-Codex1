# 950-Codex1

Table rendering utilities and supporting scripts.

## Overview

The main entry point is the `table_tool` Python package (`python -m table_tool`), which turns delimited text into an aligned table. Text borders are used by default and you can opt into Unicode box-drawing characters. The project ships with automated tests plus helper scripts under `scripts/` (for example, `vdiff2.sh` for comparing recent RCS revisions).

## Usage

Render a table from a file (commands assume you run from the project root with `PYTHONPATH=src` so the package can be discovered):

```bash
PYTHONPATH=src python3 -m table_tool path/to/data.txt
```

Read from standard input instead:

```bash
echo "left|right" | PYTHONPATH=src python3 -m table_tool -
```

The script emits formatted table output to stdout and reports validation errors to stderr (e.g., missing files or empty input).

Use `-d`/`--delimiter` to choose a different single-character separator. The default is `|`, and the allowed values are space (`" "`), `-`, `/`, `|`, and `,`:

```bash
PYTHONPATH=src python3 -m table_tool -d , path/to/data.csv
```

Use `-b`/`--thick-border-interval` to insert a thicker border (drawn with `=`) after every _n_ data rows. The default value is `3`; set it to `0` to disable thicker separators or to `x` to suppress borders completely:

```bash
PYTHONPATH=src python3 -m table_tool -b 5 path/to/data.txt
# no borders at all
PYTHONPATH=src python3 -m table_tool -b x path/to/data.txt
```

Pass `-t`/`--transpose` to swap rows and columns before rendering:

```bash
PYTHONPATH=src python3 -m table_tool -t path/to/data.txt
```

Select a border style with `-s`/`--style` (`t` for ASCII text, `g` for Unicode box drawing, 'm' for minimal decoration):

```bash
# Explicitly select ASCII (default)
PYTHONPATH=src python3 -m table_tool -s t path/to/data.txt

# Unicode borders
PYTHONPATH=src python3 -m table_tool -s g path/to/data.txt
```

Strip borders and paddings from an existing table to recover delimited data with `-r`/`--remove`. The tool auto-detects whether the input uses ASCII or Unicode borders, but you can still pass `-s` to override it:

```bash
# Convert a rendered table back into comma-delimited rows
PYTHONPATH=src python3 -m table_tool -r -d , formatted-table.txt
```

## Development

Install dependencies and run tests with [uv](https://github.com/astral-sh/uv):

```bash
uv run python -m pytest
```

RCS is used for version control at the file level. New and modified files are checked in with `ci -l <file>`, which keeps the working copy locked for further edits. Script-specific documentation (including `vdiff2.sh` and `get-prompts.sh`) lives in `scripts/README.md`.

## Roadmap

- (done) Add a `-d` option to configure the input delimiter (default `|`).
- (done) Support thicker borders after every _n_ rows; column grouping is still pending.
- (done) Offer an option to use extended graphics characters.
- (done) Provide a transpose mode for rotating the table output.
