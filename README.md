# 950-Codex1

Unicode table rendering utilities and supporting scripts.

## Overview

The main entry point is `950-010-table.py`, a command-line tool that turns delimited text into an aligned table using Unicode box-drawing characters. The project ships with automated tests plus a helper script, `vdiff2.sh`, for comparing recent RCS revisions.

## Usage

Render a table from a file:

```bash
python3 950-010-table.py path/to/data.txt
```

Read from standard input instead:

```bash
echo "left|right" | python3 950-010-table.py -
```

The script emits formatted Unicode output to stdout and reports validation errors to stderr (e.g., missing files or empty input).

Use `-d`/`--delimiter` to choose a different single-character separator. The default is `|`, and the allowed values are space (`" "`), `-`, `/`, `|`, and `,`:

```bash
python3 950-010-table.py -d , path/to/data.csv
```

Use `-b`/`--thick-border-interval` to insert a thicker border (drawn with `=`) after every _n_ data rows. The default value is `3`; set it to `0` to disable thicker separators or to `x` to suppress borders completely:

```bash
python3 950-010-table.py -b 5 path/to/data.txt
# no borders at all
python3 950-010-table.py -b x path/to/data.txt
```

## Development

Install dependencies and run tests with [uv](https://github.com/astral-sh/uv):

```bash
uv run python -m pytest
```

RCS is used for version control at the file level. New and modified files are checked in with `ci -l <file>`, which keeps the working copy locked for further edits.

The helper script `vdiff2.sh` opens `vimdiff` on the two most recent RCS revisions of a file:

```bash
./vdiff2.sh 950-010-table.py
```

## Roadmap

- (done) Add a `-d` option to configure the input delimiter (default `|`).
- (done) Support thicker borders after every _n_ rows; column grouping is still pending.
- (done) Offer an option to use extended graphics characters.
- Provide a transpose mode for rotating the table output.
