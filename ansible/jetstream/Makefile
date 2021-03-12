help:
	@echo "USAGE: make [cluster|cleanup]"
	
helm:
	ansible-playbook provision.yml --tags ubuntu -e type=helm -e people=keith -e ifile=helm.ini -e flavor=m1.medium
	
cluster:
	ansible-playbook provision.yml -e ifile=cluster.ini
	ansible-playbook -i inventories/cluster.ini reboot.yml
	
clean_helm:
	ansible-playbook cleanup.yml --tags ubuntu -e type=helm -e people=keith
	
clean_cluster:
	ansible-playbook cleanup.yml 

bare:
	ansible-playbook provision.yml --tags network,ubuntu -e type=bare -e flavor=m1.quad -e ifile=bare.ini
	
clean_bare:
	ansible-playbook cleanup.yml -e type=bare