from settings import *
from provider import *

def run():
    images = provider.compute.images.find(label="*-CentOS7-*")
    if len(images) == 0:
        print("No images found")
    else:
        for image in images:
            print(image.id)

    for image in provider.compute.images.list():
        print(f"{image.id} - {image.label}")

    # exit(0)

    networks = provider.networking.networks.find(label=network_name)
    if networks is None:
        print("Network not found")
    else:
        print(f"Found {len(networks)} networks.")
        for network in networks:
            print(f"Network {network.label} {network}")


    # network = provider.networking.networks.get('c8406076-8170-4358-abcc-41ef059392f4')
    # print(network.subnets.find(label=subnet_name)[0].label)

if __name__ == "__main__":
    run()

# network = provider.networking.networks.create(cidr_block='10.0.0.0/16', label='ks-test-network-feb17')
# print(network)
# networks = provider.networking.networks.list()
# if networks is None:
#     print("Network not found")
# else:
#     print(f"Found {len(networks)} networks.")
#     for network in networks:
#         print(f"Network {network.label} {network.id}")

# walls = provider.security.vm_firewalls.list() #('37d6a311-7be9-4ab2-858c-9bef77900d2f')
# for fw in walls:
#     print(f"{fw.id} {fw.label} {fw.name}")
#
# print(provider.security.vm_firewalls.find(label="release-testing"))

#
# routers = provider.networking.routers.list()
# if routers is None:
#     print("No router found.")
# else:
#     print(f"Found {len(routers)} routers")
#     for router in routers:
#         print(f"Router {router.label} {router.id}")
#
# print(provider.networking.routers.get('472ecf62-7d6b-4456-9b9e-ac25ebbec010'))
#
# for net in provider.neutron.list_networks('public'):
#     print(net)
