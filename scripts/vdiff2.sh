#!/usr/bin/env bash
# $Source: /srv/950-Codex1/scripts/RCS/vdiff2.sh,v $
# $Date: 2025/10/29 18:32:33 $
# $Revision: 1.2 $
# $State: Exp $

set -euo pipefail

usage() {
    echo "Usage: $0 [-w] [-r revision] [-r revision] <file> [other-file]" >&2
    exit 1
}

compare_working=false
declare -a requested_revisions=()

while getopts ":wr:" opt; do
    case "$opt" in
        w) compare_working=true ;;
        r) requested_revisions+=("$OPTARG") ;;
        *) usage ;;
    esac
done
shift $((OPTIND - 1))

rev_count=${#requested_revisions[@]}
if [ "$rev_count" -gt 2 ]; then
    echo "error: -r may be provided at most twice" >&2
    usage
fi

if [ $# -lt 1 ]; then
    usage
fi

file_args=("$@")
file_count=${#file_args[@]}

if [ "$rev_count" -gt 0 ] && [ "$file_count" -ne 1 ]; then
    echo "error: specify exactly one file when using -r" >&2
    usage
fi

if [ "$rev_count" -eq 0 ] && [ "$file_count" -gt 2 ]; then
    echo "error: provide at most two files when no revisions are specified" >&2
    usage
fi

if $compare_working && [ "$file_count" -gt 1 ]; then
    echo "error: -w cannot be used when comparing two separate files" >&2
    usage
fi

if $compare_working && [ "$rev_count" -eq 2 ]; then
    echo "error: -w cannot be combined with two revisions" >&2
    usage
fi

ensure_file_exists() {
    local file=$1
    if [ ! -f "$file" ]; then
        echo "error: file '$file' does not exist" >&2
        exit 1
    fi
}

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

if [ "$rev_count" -eq 0 ] && [ "$file_count" -eq 2 ]; then
    file_a=${file_args[0]}
    file_b=${file_args[1]}
    ensure_file_exists "$file_a"
    ensure_file_exists "$file_b"
    vimdiff "$file_a" "$file_b"
    exit 0
fi

target_file=${file_args[0]}
ensure_file_exists "$target_file"

if ! rlog_output=$(rlog "$target_file" 2>/dev/null); then
    echo "Failed to read RCS history for $target_file" >&2
    exit 1
fi

mapfile -t revisions < <(printf '%s\n' "$rlog_output" | awk '/^revision / { print $2 }')

if [ ${#revisions[@]} -eq 0 ]; then
    echo "No revisions found in RCS history for $target_file" >&2
    exit 1
fi

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

diff_paths=()

checkout_revision() {
    local rev=$1
    local dest=$2
    co -p -r"$rev" "$target_file" >"$dest"
}

if [ "$rev_count" -eq 0 ]; then
    # Compare working file with the most recent revision.
    latest_rev=${revisions[0]}
    latest_file="$tmpdir/${target_file##*/}.$latest_rev"
    checkout_revision "$latest_rev" "$latest_file"
    diff_paths=("$latest_file" "$target_file")
elif [ "$rev_count" -eq 1 ]; then
    rev=${requested_revisions[0]}
    ensure_revision_exists "$rev"
    rev_file="$tmpdir/${target_file##*/}.$rev"
    checkout_revision "$rev" "$rev_file"
    if $compare_working; then
        diff_paths=("$rev_file" "$target_file")
    else
        rev_index=$(find_revision_index "$rev") || exit 1
        if [ $((rev_index + 1)) -ge ${#revisions[@]} ]; then
            echo "Revision '$rev' has no previous revision to compare against" >&2
            exit 1
        fi
        prev_rev=${revisions[$((rev_index + 1))]}
        prev_file="$tmpdir/${target_file##*/}.$prev_rev"
        checkout_revision "$prev_rev" "$prev_file"
        diff_paths=("$prev_file" "$rev_file")
    fi
else
    rev_a=${requested_revisions[0]}
    rev_b=${requested_revisions[1]}
    ensure_revision_exists "$rev_a"
    ensure_revision_exists "$rev_b"
    file_a="$tmpdir/${target_file##*/}.$rev_a"
    file_b="$tmpdir/${target_file##*/}.$rev_b"
    checkout_revision "$rev_a" "$file_a"
    checkout_revision "$rev_b" "$file_b"
    diff_paths=("$file_a" "$file_b")
fi

vimdiff "${diff_paths[@]}"
