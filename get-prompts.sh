# $Source: /srv/950-Codex1/RCS/get-prompts.sh,v $
# $Date: 2025/10/20 20:15:20 $
# $Revision: 1.2 $
# $State: Exp $

SESSIONFILE=$1
TODAY=$(date +"%Y-%m-%d")
grep "$TODAY" "$SESSIONFILE" |
grep -E '"type":"user_message"'  |
    grep -Eo '"message":.*'|cut -d: -f2|sed 's/\\//g;s/,"kind.*/\n/' |
    fold -s


