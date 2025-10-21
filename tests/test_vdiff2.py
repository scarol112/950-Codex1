from __future__ import annotations

import os
import subprocess
from pathlib import Path
from textwrap import dedent

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = PROJECT_ROOT / "scripts" / "vdiff2.sh"


def collect_revisions(file_path: Path) -> list[str]:
    output = subprocess.check_output(
        ["rlog", str(file_path)],
        cwd=PROJECT_ROOT,
        text=True,
    )
    return [line.split()[1] for line in output.splitlines() if line.startswith("revision ")]


@pytest.fixture()
def stub_env(tmp_path: Path) -> tuple[dict[str, str], Path]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()

    log_path = tmp_path / "vimdiff.log"

    stub = bin_dir / "vimdiff"
    stub.write_text(
        dedent(
            """\
            #!/usr/bin/env bash
            set -euo pipefail
            log="${VDIFF2_LOG:?}"
            printf 'ARGS:%s\n' "$*" >>"$log"
            for file in "$@"; do
                printf 'FILE:%s\n' "$file" >>"$log"
                if [ -f "$file" ]; then
                    printf 'CONTENT:%s\n' "$(cat "$file")" >>"$log"
                else
                    printf 'MISSING:%s\n' "$file" >>"$log"
                fi
            done
            """
        )
    )
    stub.chmod(0o755)

    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
    env["VDIFF2_LOG"] = str(log_path)
    return env, log_path


def read_logged_files(log_path: Path) -> list[str]:
    if not log_path.exists():
        return []
    return [
        line.partition("FILE:")[2]
        for line in log_path.read_text().splitlines()
        if line.startswith("FILE:")
    ]


def extract_revision(path: str, target_name: str) -> str | None:
    name = Path(path).name
    prefix = f"{target_name}."
    if name.startswith(prefix):
        return name[len(prefix) :]
    return None


def is_working_file_path(path: str, target: Path) -> bool:
    candidate = Path(path)
    if candidate.is_absolute():
        try:
            return candidate.resolve() == target.resolve()
        except FileNotFoundError:
            return False
    target_name = target.name
    return candidate == Path(target_name)


def run_script(args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(SCRIPT), *args],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_default_uses_two_latest_revisions(stub_env: tuple[dict[str, str], Path]) -> None:
    env, log_path = stub_env
    revisions = collect_revisions(PROJECT_ROOT / "950-010-table.py")
    assert len(revisions) >= 2

    result = run_script(["950-010-table.py"], env)

    assert result.returncode == 0
    files = read_logged_files(log_path)
    assert len(files) == 2
    target_name = Path("950-010-table.py").name
    revisions_seen = {
        extract_revision(path, target_name)
        for path in files
        if extract_revision(path, target_name)
    }
    assert revisions_seen == {revisions[0], revisions[1]}


def test_single_revision_compares_with_previous(stub_env: tuple[dict[str, str], Path]) -> None:
    env, log_path = stub_env
    revisions = collect_revisions(PROJECT_ROOT / "950-010-table.py")
    target_rev = revisions[0]
    previous_rev = revisions[1]

    result = run_script(["950-010-table.py", target_rev], env)

    assert result.returncode == 0
    files = read_logged_files(log_path)
    target_name = Path("950-010-table.py").name
    revisions_seen = {
        extract_revision(path, target_name)
        for path in files
        if extract_revision(path, target_name)
    }
    assert revisions_seen == {target_rev, previous_rev}


def test_two_explicit_revisions(stub_env: tuple[dict[str, str], Path]) -> None:
    env, log_path = stub_env
    revisions = collect_revisions(PROJECT_ROOT / "950-010-table.py")
    assert len(revisions) >= 3
    rev_one = revisions[2]
    rev_two = revisions[3] if len(revisions) > 3 else revisions[1]

    result = run_script(["950-010-table.py", rev_one, rev_two], env)

    assert result.returncode == 0
    files = read_logged_files(log_path)
    target_name = Path("950-010-table.py").name
    revisions_seen = {
        extract_revision(path, target_name)
        for path in files
        if extract_revision(path, target_name)
    }
    assert revisions_seen == {rev_one, rev_two}


def test_working_copy_vs_latest_revision(stub_env: tuple[dict[str, str], Path]) -> None:
    env, log_path = stub_env
    revisions = collect_revisions(PROJECT_ROOT / "950-010-table.py")
    latest_rev = revisions[0]

    result = run_script(["-w", "950-010-table.py"], env)

    assert result.returncode == 0
    files = read_logged_files(log_path)
    assert len(files) == 2
    target_path = PROJECT_ROOT / "950-010-table.py"
    assert any(is_working_file_path(path, target_path) for path in files)
    target_name = Path("950-010-table.py").name
    revisions_seen = {
        extract_revision(path, target_name)
        for path in files
        if extract_revision(path, target_name)
    }
    assert latest_rev in revisions_seen


def test_working_copy_with_specific_revision(stub_env: tuple[dict[str, str], Path]) -> None:
    env, log_path = stub_env
    revisions = collect_revisions(PROJECT_ROOT / "950-010-table.py")
    chosen_rev = revisions[2]

    result = run_script(["-w", "950-010-table.py", chosen_rev], env)

    assert result.returncode == 0
    files = read_logged_files(log_path)
    assert len(files) == 2
    target_path = PROJECT_ROOT / "950-010-table.py"
    target_name = Path("950-010-table.py").name
    revisions_seen = {
        extract_revision(path, target_name)
        for path in files
        if extract_revision(path, target_name)
    }
    assert revisions_seen == {chosen_rev}
    assert any(is_working_file_path(path, target_path) for path in files)


def test_unknown_revision_reports_error(stub_env: tuple[dict[str, str], Path]) -> None:
    env, _ = stub_env

    result = run_script(["950-010-table.py", "9.9"], env)

    assert result.returncode != 0
    assert "Revision '9.9' not found" in result.stderr
