# Overview

There are a number of steps involved provisioning an OpenStack kubernetes cluster

# Provisioning a Cluster

Prerequisites:

1. Create a key pair or use an existing key pair available.  The `keypair.yml` playbook can be used to generate the key pair.
   `play keypair.yml`
   The private key will be saved to `~/.ssh/ks-cluster.pem`. You can change this by editing the playbook or by setting the `keypair` variable on the command line.
   `play keypair.tml -e keypair=my-keypair`
2. Create a network and security group.



# Setting up Kubernetes (RKE)

### Infrastructure Required

https://rancher.com/docs/rancher/v2.x/en/installation/resources/k8s-tutorials/infrastructure-tutorials/infra-for-rke2-ha/



https://rancher.com/docs/rancher/v2.x/en/installation/resources/k8s-tutorials/ha-rke2/

https://rancher.com/docs/rancher/v2.x/en/installation/resources/k8s-tutorials/ha-rke2/#5-configure-nginx-to-be-a-daemonset



# Install Rancher

https://rancher.com/docs/rancher/v2.x/en/installation/install-rancher-on-k8s/#3-choose-your-ssl-configuration