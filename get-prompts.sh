SESSIONFILE=$1
TODAY=$(date +"%Y-%m-%d")
grep "$TODAY" "$SESSIONFILE" |
grep -E '"type":"user_message"'  |
    grep -Eo '"message":.*'|cut -d: -f2|sed 's/\\//g;s/,"kind.*/\n/' |
    fold -s


