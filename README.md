# Setting up Jetstream

1. Add Jetstream credentials to ~/.cloudbridge file
1. in whatever virtualenv you're going to use, `pip install cloudbridge ipython`

Also add the following to the ~/.cloudbridge file:

```
os_zone_name = zone-r1
os_networking_zone_name = nova
```



Then to launch Launch a VM on Jetstream. I have this script which I use to launch resources on openstack/jetstream: (the only things you would need to worry about is the location of the keypair and the prefix/suffix names for the resources)

```
from cloudbridge.factory import CloudProviderFactory
from cloudbridge.factory import ProviderList
from cloudbridge.interfaces.exceptions import DuplicateResourceException

suffix = "-feb3-kc"
provider = CloudProviderFactory().create_provider(ProviderList.OPENSTACK, {})

os_image_id = '46794408-6a80-44b1-bf5a-405127753f43'
img = provider.compute.images.get(os_image_id)
print(img)

os_vm_type = 'm1.medium'

import os
try:
    kp = provider.security.key_pairs.create('am-os-kp'+suffix)
    with open('../am-os-kp.pem' + suffix, 'w') as f:
        f.write(kp.material)
    os.chmod('../am-os-kp.pem' + suffix, 0o400)
    print(kp)
except DuplicateResourceException as e:
    if not os.path.exists('../am-os-kp.pem'+suffix):
        raise e
    else:
        print("KeyPair already exists. File at: ../am-os-kp.pem" + suffix)
        kp = provider.security.key_pairs.get('am-os-kp'+suffix)
net = provider.networking.networks.create(cidr_block='10.0.0.0/16',
                                          label='am-cb-network' + suffix)
print(net)
sn = net.subnets.create(
    cidr_block='10.0.0.0/28', label='am-cb-subnet'+suffix)
print(sn)
router = provider.networking.routers.create(network=net, label='am-cb-router'+suffix)
print(router)
router.attach_subnet(sn)
print("attached subnet")
from cloudbridge.providers.openstack.resources import OpenStackInternetGateway
gw_net = provider.neutron.list_networks(name='public').get('networks')[0]
gateway = OpenStackInternetGateway(provider, gw_net)
print(gateway)
router.attach_gateway(gateway)
print("attached gateway")

from cloudbridge.interfaces.resources import TrafficDirection
fw = provider.security.vm_firewalls.create(
    label='am-cb-firewall' +suffix, description='A VM firewall used by CloudBridge', network=net)
print(fw)
fw.rules.create(TrafficDirection.INBOUND, 'tcp', 22, 22, '0.0.0.0/0')
fw.rules.create(TrafficDirection.INBOUND, 'tcp', 443, 443, '0.0.0.0/0')
fw.rules.create(TrafficDirection.INBOUND, 'tcp', 4430, 4430, '0.0.0.0/0')
fw.rules.create(TrafficDirection.INBOUND, 'tcp', 80, 80, '0.0.0.0/0')
fw.rules.create(TrafficDirection.INBOUND, 'tcp', 8080, 8080, '0.0.0.0/0')
print(list(fw.rules))
inst = provider.compute.instances.create(
    image=img, vm_type=os_vm_type, label='am-cb-instance'+suffix,
    subnet=sn, key_pair=kp, vm_firewalls=[fw])
print(inst)
# Wait until ready
inst.wait_till_ready()  # This is a blocking call
# Show instance state
inst.state

if not inst.public_ips:
    fip = gateway.floating_ips.create()
    inst.add_floating_ip(fip)
    inst.refresh()
inst.public_ips

print(inst.state)
print(inst.public_ips)
```
Which creates all the necessary resources (network, subnet, firewall, router, IP, VM) and finishes by printing the public IP attached to the launched VM.
I usually launch the script with ipython, i.e. `ipython -i launch-script.py` and keep that terminal open as a reminder to cleanup when I'm done with this VM. When I'm done and want to tear it down, I paste the following in the ipython session and it cleans up all the resources created by the script:
```
inst.delete()
fw.delete()
router.detach_gateway(gateway)
router.detach_subnet(sn)
gateway.delete()
router.delete()
sn.delete()
net.delete()
```
Finally, for the actual using of the VM in between launching and deleting:
```
git clone https://github.com/CloudVE/cloudman-boot
cd cloudman-boot
```
then in inventory/sample.ini (https://github.com/CloudVE/cloudman-boot/blob/master/inventory/sample.ini) remove all the existing IPs, add the one IP from the launched VM under both controllers and agents, and change the path to ansible_ssh_private_key_file to be wherever the kp was created for that VM. Then run the playbook as
```
ansible-playbook -i inventory/sample.ini playbook.yml
```
In a few minutes there will be a cluster running on that VM. If you ssh into it, you can run kubectl commands there directly

also if you want to also have a rancher dashboard in the cluster, optionally run:
```
kubectl create namespace cattle-system
helm repo add rancher https://releases.rancher.com/server-charts/stable
helm repo update
helm install -n cattle-system rancher rancher/rancher --set hostname=rancher.[your-ip].xip.io --set ingress.tls.source=letsEncrypt --set letsEncrypt.email="admin@cloudve.org" --set letsEncrypt.environment="production" --set letsEncrypt.ingress.class=nginx
```
in the cluster and you'll get a rancher dashboard at https://rancher.[your-ip].xip.io;