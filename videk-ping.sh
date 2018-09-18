#!/usr/bin/env bash

export SSH_AUTH_SOCK=/root/ssh-agent

PING=`timeout 300 ansible 'all:!local' -m ping | grep "=> {"`

HOSTS=`cat /etc/ansible/hosts`

NODES=(`echo "$PING" | cut -d' ' -f1,3 --output-delimiter=';'`)

if [ "${#NODES[@]}" -eq 0 ]; then
    echo "Must be more than 0 nodes!"
    exit
fi

for NODE in "${NODES[@]}"; do
    NAME=`echo $NODE | cut -d';' -f1 | tr '.' '-'`
    GROUP=`echo "${NAME%-*}"`
    PREFIX=`echo "$HOSTS" | grep -o -P "(?<=\[).*(?="$GROUP")"`

    if [ $(echo "$PREFIX" | wc -l) -ne "1" ]; then
        while read -r line; do
            HOST="$line""$NAME"
            STATUS=`echo $NODE | cut -d';' -f2`
            NODE=`curl -s -X GET "http://localhost:3000/api/nodes/?name=$HOST"`
            ID="$(echo "$NODE" | grep -Po '"_id":(\d*?,|.*?[^\\]")' | cut -d'"' -f4)"
            MID="$(echo "$NODE" | grep -Po '"machine_id":(\d*?,|.*?[^\\]")' | cut -d'"' -f4)"
            echo "--------inactive"
            echo "$HOST"
            echo "$STATUS"
            curl -s -H "Content-Type: application/json" -X PUT -d \
              '{"status":"inactive","name":"tmp-'"$MID"'"}' "http://localhost:3000/api/nodes/$ID"
            echo -e "\n\n"
        done <<< "$PREFIX"
    else
        HOST="$PREFIX""$NAME"
        STATUS=`echo $NODE | cut -d';' -f2`
        NODE=`curl -s -X GET "http://localhost:3000/api/nodes/?name=$HOST"`
        ID="$(echo "$NODE" | grep -Po '"_id":(\d*?,|.*?[^\\]")' | cut -d'"' -f4)"
        MID="$(echo "$NODE" | grep -Po '"machine_id":(\d*?,|.*?[^\\]")' | cut -d'"' -f4)"

        if [ "$STATUS" = "SUCCESS" ]; then
            echo "--------active"
            echo "$HOST"
            echo "$STATUS"
            curl -s -H "Content-Type: application/json" -X PUT -d \
            '{"status":"active"}' "http://localhost:3000/api/nodes/$ID"
        else
            echo "--------inactive"
            echo "$HOST"
            echo "$STATUS"
            curl -s -H "Content-Type: application/json" -X PUT -d \
              '{"status":"inactive","name":"tmp-'"$MID"'"}' "http://localhost:3000/api/nodes/$ID"
        fi
        echo ""
    fi
    echo ""
done
