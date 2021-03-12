#!/usr/bin/env bash
for n in `cat inventories/galaxy.ini | grep _host | cut -d\- -f1` ; do 
	ip=`cat inventories/galaxy.ini | grep $n | cut -d= -f2`
	echo "$n -> http://$ip"
done
