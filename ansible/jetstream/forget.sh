#!/usr/bin/env bash

if [[ -z "$KEY" ]] ; then
	KEY=~/.ssh/ks-cluster.pem
fi

INV=inventory.ini
if [[ -n  "$1" ]] ; then
	INV=$1
fi

function connect_to_server() {
	for tries in 1 2 3 4 5 ; do
		echo "$tries) Attempting an SSH connection to $1"
		ssh -i $KEY -o "StrictHostKeyChecking no" ubuntu@$1 uname -a
		if [[ $? = 0 ]] ; then	
			return
		fi
		echo "Pausing"
		sleep 10
	done
	echo "Unable to SSH to $1"
	exit 1
}

for ip in $(cat $INV | grep _host | cut -d= -f2) ; do
	ssh-keygen -R $ip
	#ssh -i ~/.ssh/ks-cluster.pem -o "StrictHostKeyChecking no" ubuntu@$ip uname -a
	connect_to_server $ip
done
