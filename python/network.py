from settings import AWS
# from provider import *
from cloudbridge.interfaces.resources import TrafficDirection

def provision_network(cloud, name):
    cloud = AWS('ks', 'testing')
    network = cloud.provider.networking.networks.create(cidr_block='10.0.0.0/16', label=cloud.network)
    print(network)
    subnet = network.subnets.create(
        cidr_block='10.0.0.0/28', label=cloud.subnet)
    print(subnet)

    router = cloud.provider.networking.routers.create(network=network, label=cloud.project)
    print(router)
    router.attach_subnet(subnet)
    print("attached subnet")

    gateway = get_gateway()
    print(gateway)
    router.attach_gateway(gateway)
    print("attached gateway")

    walls = cloud.provider.security.vm_firewalls.find(label=cloud.firewall)
    if walls is None or len(walls) == 0:
        fw = cloud.provider.security.vm_firewalls.create(
            label=cloud.firewall, description='Firewall rules for the release-testing network', network=cloud.network)
        print(fw)
        fw.rules.create(TrafficDirection.INBOUND, 'tcp', 22, 22, '0.0.0.0/0')
        fw.rules.create(TrafficDirection.INBOUND, 'tcp', 443, 443, '0.0.0.0/0')
        fw.rules.create(TrafficDirection.INBOUND, 'tcp', 4430, 4430, '0.0.0.0/0')
        fw.rules.create(TrafficDirection.INBOUND, 'tcp', 80, 80, '0.0.0.0/0')
        fw.rules.create(TrafficDirection.INBOUND, 'tcp', 8080, 8080, '0.0.0.0/0')

if __name__ == "__main__":
    provision_network()

