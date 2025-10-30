# Scripts

This directory collects auxiliary command-line helpers used alongside the Python
table renderer.

## `vdiff2.sh`

Wrapper around `vimdiff` for inspecting RCS-tracked files.

```
Usage: vdiff2.sh [-w] [-r revision] [-r revision] <file> [other-file]
```

Key behaviours:

- **No `-r` flags**
  - One file: compare the working copy against its most recent RCS revision.
  - Two files: compare the files directly (no RCS lookup). `-w` is not allowed.
- **`-r` once** (must supply exactly one file)
  - Default: compare the requested revision with its immediate predecessor.
  - With `-w`: compare the requested revision against the working copy.
- **`-r` twice** (must supply exactly one file)
  - Compare the two specified revisions. Cannot be combined with `-w`.

Additional notes:

- `-r` may be provided at most twice, and combining `-r` with two file names is
  rejected.
- All revisions are resolved via `rlog`/`co`, and temporary copies are created so
  the working tree is left untouched.

### Examples

```bash
# Working copy vs latest revision
./scripts/vdiff2.sh 950-010-table.py

# Compare two working files directly
./scripts/vdiff2.sh README.md Project-structure.md

# Inspect a revision against its predecessor
./scripts/vdiff2.sh -r 1.5 950-010-table.py

# Revision vs working copy
./scripts/vdiff2.sh -w -r 1.5 950-010-table.py

# Two specific revisions
./scripts/vdiff2.sh -r 1.5 -r 1.3 950-010-table.py
```

## `get-prompts.sh`

Filters a Codex session rollout log to extract the user prompt text for the
current day. The script expects the session log path as its sole argument.

```bash
./scripts/get-prompts.sh session-log.jsonl
```

The extracted messages are unescaped and soft-wrapped for easier reading.
