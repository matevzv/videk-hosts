#!/usr/bin/env bash

PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

PING=`ansible 'all:!local' -m ping | grep "=> {"`

NODES=(`echo "$PING" | cut -d' ' -f1,3 --output-delimiter=';'`)

if [ "${#NODES[@]}" -eq 0 ]; then
    echo "Must be more than 0 nodes!"
    exit
fi

for NODE in "${NODES[@]}"; do
    NAME=`echo $NODE | cut -d';' -f1 | tr '.' '-'`
    STATUS=`echo $NODE | cut -d';' -f2`
    NODE=`curl -s -X GET "http://localhost/api/nodes/?name=$NAME"`
    ID="$(echo "$NODE" | grep -Po '"_id":(\d*?,|.*?[^\\]")' | cut -d'"' -f4)"

    if [ "$STATUS" = "SUCCESS" ]; then
      echo "--------active"
      echo "$NAME"
      echo "$STATUS"
      curl -s -H "Content-Type: application/json" -X PUT -d \
      '{"status":"active"}' "http://localhost/api/nodes/$ID"
    else
      echo "--------inactive"
      echo "$NAME"
      echo "$STATUS"
      curl -s -H "Content-Type: application/json" -X PUT -d \
      '{"status":"inactive"}' "http://localhost/api/nodes/$ID"
    fi
    echo $'\n'
done
