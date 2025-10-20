from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = PROJECT_ROOT / "950-010-table.py"


def run_script(*args: str, input_data: str | None = None) -> subprocess.CompletedProcess[str]:
    """Run the table script with the provided arguments and captured IO."""
    cmd = [sys.executable, str(SCRIPT_PATH), *args]
    return subprocess.run(
        cmd,
        input=input_data,
        text=True,
        capture_output=True,
        check=False,
    )


def test_table_single_file(tmp_path: Path) -> None:
    input_path = tmp_path / "input.txt"
    input_path.write_text("a|bbbbb|c\n1|2|3\n", encoding="utf-8")

    result = run_script(str(input_path))

    expected_output = "\n".join(
        [
            "┌───┬───────┬───┐",
            "│ a │ bbbbb │ c │",
            "├───┼───────┼───┤",
            "│ 1 │ 2     │ 3 │",
            "└───┴───────┴───┘",
            "",
        ]
    )

    assert result.returncode == 0
    assert result.stdout == expected_output
    assert result.stderr == ""


def test_table_from_stdin() -> None:
    result = run_script("-", input_data="left|right\n")

    expected_output = "\n".join(
        [
            "┌──────┬───────┐",
            "│ left │ right │",
            "└──────┴───────┘",
            "",
        ]
    )

    assert result.returncode == 0
    assert result.stdout == expected_output
    assert result.stderr == ""


def test_no_borders(tmp_path: Path) -> None:
    input_path = tmp_path / "plain.txt"
    input_path.write_text("c1|c2\n1|1\n2|2\n", encoding="utf-8")

    result = run_script("-b", "x", str(input_path))

    expected_output = "\n".join(
        [
            "c1 c2",
            "1  1",
            "2  2",
            "",
        ]
    )

    assert result.returncode == 0
    assert result.stdout == expected_output
    assert result.stderr == ""


def test_missing_file_reports_error(tmp_path: Path) -> None:
    missing_path = tmp_path / "nope.txt"

    result = run_script(str(missing_path))

    assert result.returncode == 1
    assert "error" in result.stderr
    assert "does not exist" in result.stderr


def test_empty_input_emits_error(tmp_path: Path) -> None:
    empty_path = tmp_path / "empty.txt"
    empty_path.write_text("\n", encoding="utf-8")

    result = run_script(str(empty_path))

    assert result.returncode == 1
    assert "no rows found" in result.stderr


def test_custom_delimiter_comma(tmp_path: Path) -> None:
    input_path = tmp_path / "comma.txt"
    input_path.write_text("name,age\nAlice,30\n", encoding="utf-8")

    result = run_script("-d", ",", str(input_path))

    expected_output = "\n".join(
        [
            "┌───────┬─────┐",
            "│ name  │ age │",
            "├───────┼─────┤",
            "│ Alice │ 30  │",
            "└───────┴─────┘",
            "",
        ]
    )

    assert result.returncode == 0
    assert result.stdout == expected_output
    assert result.stderr == ""


def test_invalid_delimiter_is_rejected(tmp_path: Path) -> None:
    input_path = tmp_path / "data.txt"
    input_path.write_text("a;b\n", encoding="utf-8")

    result = run_script("-d", ";", str(input_path))

    assert result.returncode == 2
    assert "invalid choice" in result.stderr


def test_thick_border_default_interval(tmp_path: Path) -> None:
    input_path = tmp_path / "thick.txt"
    input_path.write_text("c1|c2\n1|1\n2|2\n3|3\n4|4\n", encoding="utf-8")

    result = run_script(str(input_path))

    expected_output = "\n".join(
        [
            "┌────┬────┐",
            "│ c1 │ c2 │",
            "├────┼────┤",
            "│ 1  │ 1  │",
            "├────┼────┤",
            "│ 2  │ 2  │",
            "╞════╪════╡",
            "│ 3  │ 3  │",
            "├────┼────┤",
            "│ 4  │ 4  │",
            "└────┴────┘",
            "",
        ]
    )

    assert result.returncode == 0
    assert result.stdout == expected_output
    assert result.stderr == ""


def test_thick_border_disabled(tmp_path: Path) -> None:
    input_path = tmp_path / "thin.txt"
    input_path.write_text("c1|c2\n1|1\n2|2\n3|3\n4|4\n", encoding="utf-8")

    result = run_script("-b", "0", str(input_path))

    expected_output = "\n".join(
        [
            "┌────┬────┐",
            "│ c1 │ c2 │",
            "├────┼────┤",
            "│ 1  │ 1  │",
            "├────┼────┤",
            "│ 2  │ 2  │",
            "├────┼────┤",
            "│ 3  │ 3  │",
            "├────┼────┤",
            "│ 4  │ 4  │",
            "└────┴────┘",
            "",
        ]
    )

    assert result.returncode == 0
    assert result.stdout == expected_output
    assert result.stderr == ""
