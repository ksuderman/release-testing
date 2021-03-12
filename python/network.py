from settings import *
from provider import *
from cloudbridge.interfaces.resources import TrafficDirection

def provision_network():
    network = provider.networking.networks.create(cidr_block='10.0.0.0/16', label=network_name)
    print(network)
    subnet = network.subnets.create(
        cidr_block='10.0.0.0/28', label=subnet_name)
    print(subnet)

    router = provider.networking.routers.create(network=network, label=router_name)
    print(router)
    router.attach_subnet(subnet)
    print("attached subnet")

    gateway = get_gateway()
    print(gateway)
    router.attach_gateway(gateway)
    print("attached gateway")

    walls = provider.security.vm_firewalls.find(label=firewall_name)
    if walls is None or len(walls) == 0:
        fw = provider.security.vm_firewalls.create(
            label=firewall_name, description='Firewall rules for the release-testing network', network=network_name)
        print(fw)
        fw.rules.create(TrafficDirection.INBOUND, 'tcp', 22, 22, '0.0.0.0/0')
        fw.rules.create(TrafficDirection.INBOUND, 'tcp', 443, 443, '0.0.0.0/0')
        fw.rules.create(TrafficDirection.INBOUND, 'tcp', 4430, 4430, '0.0.0.0/0')
        fw.rules.create(TrafficDirection.INBOUND, 'tcp', 80, 80, '0.0.0.0/0')
        fw.rules.create(TrafficDirection.INBOUND, 'tcp', 8080, 8080, '0.0.0.0/0')

if __name__ == "__main__":
    provision_network()

