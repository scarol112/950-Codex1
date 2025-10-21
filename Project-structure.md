# Recommended Project Layout

This repository mixes Python utilities with supporting shell scripts. The directory
structure below keeps responsibilities clear while making it easy to discover code,
tests, and documentation.

```
.
├── src/                  # Python packages and modules
│   └── <package>/        # Application/library code
├── scripts/              # Executable shell helpers (vdiff2, etc.)
├── tests/                # Pytest suite and fixtures
├── docs/                 # Additional documentation (optional)
├── Project-structure.md  # This file
├── pyproject.toml        # Python dependency metadata
├── README.md             # Project overview and usage
├── uv.lock               # Resolver lock file
└── Makefile / justfile   # Task automation (optional)
```

### Python code (`src/`)
- Place importable modules under `src/` to avoid conflicts with tooling.
- If the project is a single script, add a package directory (e.g., `src/table_tool/`)
  and expose entry points in `__main__.py` or a CLI module.

### Shell scripts (`scripts/`)
- Keep shell utilities in `scripts/` with executable permissions.
- Prefer descriptive filenames and POSIX-compliant shebangs (`#!/usr/bin/env bash`).

### Tests (`tests/`)
- Mirror the package structure for unit tests.
- Use fixtures for command-line integrations and isolate filesystem writes to temporary
  directories.

### Documentation
- `README.md` for quickstart instructions.
- `docs/` (if needed) for expanded guides or design notes.

This layout separates runtime code from tooling, encourages packaging best practices, and
keeps cross-language assets organized.
