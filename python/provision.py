import os
import yaml
import datetime
from provider import *
import network

from cloudbridge.interfaces.resources import TrafficDirection
from cluster import ClusterData
from settings import *

suffix = datetime.datetime.now().strftime("%b%d").lower()

def find_resource(resource, label):
    things = resource.find(label=label)
    if len(things) == 0:
        return None
    return things[0]

def find_firewall():
    # walls = provider.security.vm_firewalls.find(label=firewall_name)
    # if walls is None or len(walls) == 0:
    #     return None
    # return walls[0]
    return find_resource(provider.security.vm_firewalls, firewall_name)

def find_subnet():
    network = find_resource(provider.networking.networks, network_name)
    if network is None:
        return None
    return find_resource(network.subnets, subnet_name)

def provision_cluster():
    fw = find_firewall()
    if fw is None:
        print("Unable to locate the firewall")
        return
    print(f"Using firewall {fw.label}")
    # print(list(fw.rules))

    subnet = find_subnet()
    if subnet is None:
        print("Unable to locate the subnet")
    print(f"Using subnet {subnet.label}")

    img = provider.compute.images.get(os_image_id)
    print(f"Using image {img.label}")

    kp = provider.security.key_pairs.get(keypair_name)
    if kp is None:
        print("Unable to find the keypair")
        return
    print(f"Keypair: {kp}")

    return
    gateway = get_gateway()
    for member in team:
        print(f"Creating instance for {member}")
        instance = provider.compute.instances.create(
            image=img, vm_type=os_vm_type, label=project_name + "-" + member,
            subnet=subnet, key_pair=kp, vm_firewalls=[fw])
        print(instance)
        # Wait until ready
        instance.wait_till_ready()  # This is a blocking call
        # Show instance state
        instance.state

        if not instance.public_ips:
            print("Assigning a public IP")
            fip = gateway.floating_ips.create()
            instance.add_floating_ip(fip)
            instance.refresh()
        # instance.public_ips
        print("Instance ready.")
        print(instance.state)
        print(instance.public_ips)

    #
    # cluster = ClusterData()
    # cluster.network = network.id
    # cluster.subnet = subnet.id
    # cluster.router = router.id
    # cluster.firewall = fw.id
    # cluster.instance = instance.id
    #
    # print(yaml.dump(cluster))


if __name__ == "__main__":
    # network.provision_network()
    provision_cluster()
