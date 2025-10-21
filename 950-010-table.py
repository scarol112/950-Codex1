#!/usr/bin/env python3
# $Source: /srv/950-Codex1/RCS/950-010-table.py,v $
# $Date: 2025/10/21 18:02:21 $
# $Revision: 1.9 $
# $State: Exp $

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List, Sequence

ALLOWED_DELIMITERS = {" ", "-", "/", "|", ","}
STYLE_DEFINITIONS = {
    "t": {
        "vertical": "|",
        "top": ("+", "+", "+", "-"),
        "middle_thin": ("+", "+", "+", "-"),
        "middle_thick": ("+", "+", "+", "="),
        "bottom_thin": ("+", "+", "+", "-"),
        "bottom_thick": ("+", "+", "+", "="),
    },
    "g": {
        "vertical": "│",
        "top": ("┌", "┬", "┐", "─"),
        "middle_thin": ("├", "┼", "┤", "─"),
        "middle_thick": ("╞", "╪", "╡", "═"),
        "bottom_thin": ("└", "┴", "┘", "─"),
        "bottom_thick": ("╘", "╧", "╛", "═"),
    },
}


def parse_border_interval(value: str) -> int | str:
    if value.lower() == "x":
        return "x"
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "thick border interval must be a non-negative integer or 'x'"
        ) from exc
    if parsed < 0:
        raise argparse.ArgumentTypeError(
            "thick border interval must be a non-negative integer or 'x'"
        )
    return parsed


def parse_style(value: str) -> str:
    key = value.lower()
    if key not in STYLE_DEFINITIONS:
        raise argparse.ArgumentTypeError("style must be 't' (text) or 'g' (graphics)")
    return key


def parse_rows(
    lines: Iterable[str],
    *,
    skip_empty: bool = True,
    delimiter: str = "|",
) -> List[List[str]]:
    rows: List[List[str]] = []
    for raw_line in lines:
        line = raw_line.rstrip("\n")
        if skip_empty and not line.strip():
            continue
        cells = [cell.strip() for cell in line.split(delimiter)]
        rows.append(cells)
    if not rows:
        raise ValueError("no rows found in the input")
    return rows


def normalise_rows(rows: Sequence[List[str]]) -> List[List[str]]:
    max_columns = max(len(row) for row in rows)
    return [row + [""] * (max_columns - len(row)) for row in rows]


def transpose_rows(rows: Sequence[Sequence[str]]) -> List[List[str]]:
    return [list(column) for column in zip(*rows)]


def column_widths(rows: Sequence[Sequence[str]]) -> List[int]:
    widths = [0] * len(rows[0])
    for row in rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(cell))
    return widths


def render_table(
    rows: Sequence[Sequence[str]],
    *,
    thick_border_interval: int | str = 3,
    style: str = "t",
) -> str:
    widths = column_widths(rows)

    if thick_border_interval == "x":
        lines = []
        for row in rows:
            padded_cells = [
                cell.ljust(width) for cell, width in zip(row, widths)
            ]
            lines.append(" ".join(padded_cells).rstrip())
        return "\n".join(lines)

    assert isinstance(thick_border_interval, int)

    style_config = STYLE_DEFINITIONS[style]
    vertical = style_config["vertical"]

    def border(style: str) -> str:
        left, mid, right, fill = style_config[style]
        segments = [fill * (width + 2) for width in widths]
        return left + mid.join(segments) + right

    lines = [border("top")]
    total_rows = len(rows)
    for row_index, row in enumerate(rows, start=1):
        padded_cells = [
            f" {cell}{' ' * (width - len(cell))} " for cell, width in zip(row, widths)
        ]
        lines.append(vertical + vertical.join(padded_cells) + vertical)
        use_thick_border = (
            thick_border_interval > 0 and row_index % thick_border_interval == 0
        )
        is_last = row_index == total_rows
        if is_last:
            style = "bottom_thick" if use_thick_border else "bottom_thin"
        else:
            style = "middle_thick" if use_thick_border else "middle_thin"
        lines.append(border(style))
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render a delimited text file as an ASCII or Unicode table."
    )
    parser.add_argument(
        "input",
        help="Path to the input file. Use '-' to read from standard input.",
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        default="|",
        choices=sorted(ALLOWED_DELIMITERS),
        help=(
            "Single-character column delimiter to parse the input. "
            "Allowed values: space, -, /, |, ,"
        ),
    )
    parser.add_argument(
        "-b",
        "--thick-border-interval",
        type=parse_border_interval,
        default=3,
        help=(
            "Insert a thicker separator every N data rows. "
            "Use 0 to disable thicker borders or 'x' to remove borders entirely "
            "(default: 3)."
        ),
    )
    parser.add_argument(
        "-t",
        "--transpose",
        action="store_true",
        help="Transpose the table before rendering, swapping rows with columns.",
    )
    parser.add_argument(
        "-s",
        "--style",
        type=parse_style,
        default="t",
        choices=sorted(STYLE_DEFINITIONS),
        help="Table style: 't' for text borders (default) or 'g' for Unicode graphics.",
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
        rows = parse_rows(lines, delimiter=args.delimiter)
        normalised_rows = normalise_rows(rows)
        table_rows = (
            transpose_rows(normalised_rows) if args.transpose else normalised_rows
        )
        table = render_table(
            table_rows,
            thick_border_interval=args.thick_border_interval,
            style=args.style,
        )
    except Exception as exc:  # noqa: BLE001
        parser.print_usage(file=sys.stderr)
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
