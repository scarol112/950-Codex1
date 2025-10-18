#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List, Sequence


def parse_rows(lines: Iterable[str], *, skip_empty: bool = True) -> List[List[str]]:
    rows: List[List[str]] = []
    for line_no, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip("\n")
        if skip_empty and not line.strip():
            continue
        cells = [cell.strip() for cell in line.split("|")]
        rows.append(cells)
    if not rows:
        raise ValueError("no rows found in the input")
    return rows


def normalise_rows(rows: Sequence[List[str]]) -> List[List[str]]:
    max_columns = max(len(row) for row in rows)
    normalised: List[List[str]] = []
    for row in rows:
        padded = row + [""] * (max_columns - len(row))
        normalised.append(padded)
    return normalised


def column_widths(rows: Sequence[Sequence[str]]) -> List[int]:
    widths = [0] * len(rows[0])
    for row in rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(cell))
    return widths


def render_table(rows: Sequence[Sequence[str]]) -> str:
    widths = column_widths(rows)

    def border(char: str = "-") -> str:
        return "+" + "+".join(char * (width + 2) for width in widths) + "+"

    lines = [border("-")]
    for row in rows:
        padded_cells = [
            f" {cell}{' ' * (width - len(cell))} " for cell, width in zip(row, widths)
        ]
        lines.append("|" + "|".join(padded_cells) + "|")
        lines.append(border("-"))
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render a pipe-delimited text file as an ASCII table."
    )
    parser.add_argument(
        "input",
        help="Path to the input file. Use '-' to read from standard input.",
    )
    return parser


def load_lines(input_path: str) -> Iterable[str]:
    if input_path == "-":
        return sys.stdin
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"input file '{input_path}' does not exist")
    return path.read_text(encoding="utf-8").splitlines(keepends=True)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        lines = load_lines(args.input)
        rows = parse_rows(lines)
        normalised_rows = normalise_rows(rows)
        table = render_table(normalised_rows)
    except Exception as exc:  # noqa: BLE001
        parser.print_usage(file=sys.stderr)
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
