#!/usr/bin/env bash

for ip in `cat inventories/galaxy.ini | grep _host | cut -d= -f2` ; do
	ssh-keygen -R $ip
	ssh -i ~/.ssh/release-testing-2101.pem ubuntu@$ip uname -a
done
