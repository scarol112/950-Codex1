#!/bin/sh
# $Source: /srv/950-Codex1/scripts/get-prompts.sh,v $
# $Date: 2025/10/21 19:18:09 $
# $Revision: 1.1 $
# $State: Exp $

SESSIONFILE=$1
TODAY=$(date +"%Y-%m-%d")
grep "$TODAY" "$SESSIONFILE" |
grep -E '"type":"user_message"'  |
    grep -Eo '"message":.*'|cut -d: -f2|sed 's/\\//g;s/,"kind.*/\n/' |
    fold -s


