#!/usr/bin/env bash
set -euo pipefail

usage() {
    echo "Usage: $0 <file>" >&2
    exit 1
}

if [ $# -ne 1 ]; then
    usage
fi

target_file=$1

if ! rlog_output=$(rlog "$target_file" 2>/dev/null); then
    echo "Failed to read RCS history for $target_file" >&2
    exit 1
fi

# Collect revisions starting from the most recent within RCS history.
mapfile -t revisions < <(printf '%s\n' "$rlog_output" | awk '/^revision / { print $2 }')

if [ ${#revisions[@]} -lt 2 ]; then
    echo "Need at least two revisions in RCS history for $target_file" >&2
    exit 1
fi

new_rev=${revisions[0]}
old_rev=${revisions[1]}

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

new_file="$tmpdir/${target_file##*/}.$new_rev"
old_file="$tmpdir/${target_file##*/}.$old_rev"

co -p -r"$new_rev" "$target_file" >"$new_file"
co -p -r"$old_rev" "$target_file" >"$old_file"

vimdiff "$old_file" "$new_file"
