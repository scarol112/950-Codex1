#!/usr/bin/env bash
# $Source: /srv/950-Codex1/scripts/vdiff2.sh,v $
# $Date: 2025/10/21 19:16:51 $
# $Revision: 1.1 $
# $State: Exp $

set -euo pipefail

usage() {
    echo "Usage: $0 [-w] <file> [revision [revision]]" >&2
    exit 1
}

compare_working=false
while getopts ":w" opt; do
    case "$opt" in
        w) compare_working=true ;;
        *) usage ;;
    esac
done
shift $((OPTIND - 1))

if [ $# -lt 1 ]; then
    usage
fi

target_file=$1
shift
rev_args=("$@")
rev_count=${#rev_args[@]}

if ! rlog_output=$(rlog "$target_file" 2>/dev/null); then
    echo "Failed to read RCS history for $target_file" >&2
    exit 1
fi

mapfile -t revisions < <(printf '%s\n' "$rlog_output" | awk '/^revision / { print $2 }')

if [ ${#revisions[@]} -eq 0 ]; then
    echo "No revisions found in RCS history for $target_file" >&2
    exit 1
fi

find_revision_index() {
    local search=$1
    local idx
    for idx in "${!revisions[@]}"; do
        if [ "${revisions[$idx]}" = "$search" ]; then
            printf '%s\n' "$idx"
            return 0
        fi
    done
    return 1
}

ensure_revision_exists() {
    local rev=$1
    if ! find_revision_index "$rev" >/dev/null; then
        echo "Revision '$rev' not found for $target_file" >&2
        exit 1
    fi
}

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

diff_paths=()

if $compare_working; then
    if [ "$rev_count" -gt 1 ]; then
        echo "Option -w accepts at most one revision argument" >&2
        exit 1
    fi
    if [ "$rev_count" -eq 1 ]; then
        rev=${rev_args[0]}
        ensure_revision_exists "$rev"
    else
        rev=${revisions[0]}
    fi
    rev_file="$tmpdir/${target_file##*/}.$rev"
    co -p -r"$rev" "$target_file" >"$rev_file"
    diff_paths=("$rev_file" "$target_file")
else
    case "$rev_count" in
        0)
            if [ ${#revisions[@]} -lt 2 ]; then
                echo "Need at least two revisions in RCS history for $target_file" >&2
                exit 1
            fi
            rev_a=${revisions[1]}
            rev_b=${revisions[0]}
            ;;
        1)
            rev_b=${rev_args[0]}
            rev_index=$(find_revision_index "$rev_b") || {
                echo "Revision '$rev_b' not found for $target_file" >&2
                exit 1
            }
            if [ $((rev_index + 1)) -ge ${#revisions[@]} ]; then
                echo "Revision '$rev_b' has no previous revision to compare against" >&2
                exit 1
            fi
            rev_a=${revisions[$((rev_index + 1))]}
            ;;
        *)
            rev_a=${rev_args[0]}
            rev_b=${rev_args[1]}
            ensure_revision_exists "$rev_a"
            ensure_revision_exists "$rev_b"
            ;;
    esac
    file_a="$tmpdir/${target_file##*/}.$rev_a"
    file_b="$tmpdir/${target_file##*/}.$rev_b"
    co -p -r"$rev_a" "$target_file" >"$file_a"
    co -p -r"$rev_b" "$target_file" >"$file_b"
    diff_paths=("$file_a" "$file_b")
fi

vimdiff "${diff_paths[@]}"
