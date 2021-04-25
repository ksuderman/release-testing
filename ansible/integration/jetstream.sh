#!/usr/bin/env bash

if [[ -z "$KEY" ]] ; then
  KEY=~/.ssh/ks-cluster.pem
fi

set -eu

BASE=~/Workspaces/JHU
JETSTREAM_PLAYBOOKS=~/Workspaces/JHU/release-testing-git/ansible/jetstream
CLOUDBOOT_PLAYBOOKS=~/Workspaces/JHU/cloudman-boot/
GALAXY_HELM_PLAYBOOK=~/Workspaces/JHU/release-testing/ansible/integration

INI=cluster.ini
INVENTORY=$JETSTREAM_PLAYBOOKS/inventories/$INI
CLUSTER_CONFIG=$JETSTREAM_PLAYBOOKS/configs/jetstream-integration.yml

echo "Writing cluster configuration $CLUSTER_CONFIG for the playbooks"
cat << EOF > $CLUSTER_CONFIG
inventory: $INI
server: ks-rke-integration
keypair: ks-cluster
master_flavor: m1.quad
flavor: m1.medium
firewall: ks-rancher-firewall
images:
  centos: 4e769e39-2ffa-4c64-99f6-404fd52cc85e
  ubuntu: 8bc9412c-e666-40fa-8254-f8481e344a49
EOF

# Provision the cluster on Jetstream
cd $JETSTREAM_PLAYBOOKS
pwd
ls
#ansible-playbook server.yml -e config=jetstream-integration
ansible-playbook cluster.yml -e config=jetstream-integration

# Establish an SSH connection to the server so nothing later complains
# about new servers or unknown certificates.
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

# Remove certificates for any recycled IP addresses and then connect to
# get the new certificate.
for ip in $(cat $INVENTORY | grep _host | cut -d= -f2) ; do
	ssh-keygen -R $ip
	connect_to_server $ip
done

# Reboot the cluster after all the nodes have finished updating.
ansible-playbook -i $INVENTORY reboot.yml

# Run the Cloudman-Boot Playbook to install RKE and Cloudman
cd $CLOUDBOOT_PLAYBOOKS
ansible-playbook -i $INVENTORY playbook.yml

# Now we can install Galaxy to the cluster
# TODO Should we be waiting on Rancher here?
cd $GALAXY_HELM_PLAYBOOK
ansible-playbook -i $INVENTORY galaxy.yml


