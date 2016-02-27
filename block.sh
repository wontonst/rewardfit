#!/bin/bash

###### DEPRECATED

set -euo pipefail

function my_trap_handler()
{
        MYSELF="$0"               # equals to my script name
        LASTLINE="$1"            # argument 1: last line of error occurence
        LASTERR="$2"             # argument 2: error code of last command
        echo "${MYSELF}: line ${LASTLINE}: exit status of last command: ${LASTERR}"

        # do additional processing: send email or SNMP trap, write result to database, etc.
}

trap 'my_trap_handler ${LINENO} $?' ERR

# This script will let the hosts file block arbitrary websites #

cp /etc/hosts.backup /etc/hosts
for i in netflix reddit facebook pornhub buzzfeed twitter
do
    echo "127.0.0.1 $i.com" >> /etc/hosts
    echo "127.0.0.1 www.$i.com" >> /etc/hosts
done

dscacheutil -flushcache
