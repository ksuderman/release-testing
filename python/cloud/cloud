#!/usr/bin/env python

from settings import *
from cloudbridge.factory import ProviderList

def network_create(cloud, options):
    if len(options) != 1:
        print("ERROR: network create expects one parameter, the name of the network to create.")
        return
    cloud.initialize(options[0])


def network_delete(cloud, options):
    if len(options) != 1:
        print("ERROR: network delete expects one parameter, the name of the network to delete.")
        return
    cloud.tear_down(options[0])


def network_list(cloud, options):
    print("Networks:")
    for net in cloud.provider.networking.networks.list():
        print(f'{net.id} - {net.label}')


def keypair_create(cloud, options):
    if len(options) != 1:
        print("ERROR: keypair create expects one parameter, the name of the keypair to create.")
        return
    cloud.get_keypair(options[0])


def keypair_delete(cloud, options):
    if len(options) != 1:
        print("ERROR: keypair delete expects one parameter, the name of the keypair to delete.")
        return
    home = os.environ.get('HOME')
    filename = options[0] + '.pem'
    path = os.path.join(home, '.ssh', filename)
    if not os.path.exists(path):
        print(f'No local key found. Refusing to delete remote keypair!')
        return

    os.remove(path)
    print(f'Deleted local key file {path}')
    cloud.provider.security.key_pairs.delete(options[0])
    print(f'Deleted keypair {options[0]}')


def keypair_list(cloud, options):
    print(cloud)
    print("Keypairs:")
    for kp in cloud.provider.security.key_pairs.list():
        print(kp)


def instance_create(cloud, options):
    print("instance_create")


def instance_delete(cloud, options):
    print("instance_delete")


def instance_list(cloud, options):
    print("instance_list")

def image_set(cloud, options):
    if len(options) != 1:
        print('ERROR: image set required one parameter, the image ID')
        return
    cloud.image = options[0]
    cloud.save_config()

def image_get(cloud, options):
    if len(options) != 0:
        print('ERROR: image get does not take any parameters')
        return
    print(f'Image ID: {cloud.image}')

def vm_set(cloud, options):
    if len(options) != 1:
        print('ERROR: vm set required one parameter, the vm type')
        return
    cloud.vm = options[0]
    cloud.save_config()

def vm_get(cloud, options):
    if len(options) != 0:
        print('ERROR: vm get does not take any parameters')
        return
    print(f'VM Type: {cloud.vm}')


handlers = {
    'network': {
        'create': network_create,
        'delete': network_delete,
        'list': network_list
    },
    'keypair': {
        'create': keypair_create,
        'delete': keypair_delete,
        'list': keypair_list
    },
    'instance': {
        'create': instance_create,
        'delete': instance_delete,
        'list': instance_list
    },
    'image': {
        'set': image_set,
        'get': image_get
    },
    'vm': {
        'set': vm_set,
        'get': vm_get
    }
}

resources = [ 'network', 'keypair', 'instance', 'cluster', 'image', 'vm']
commands = [ 'create', 'delete', 'list', 'set', 'get', 'help' ]
clouds = [ProviderList.AWS, ProviderList.GCP, ProviderList.OPENSTACK, ProviderList.MOCK]
cloud_constructors = {
    ProviderList.AWS: AWS,
    ProviderList.GCP: GCP,
    ProviderList.OPENSTACK: OpenStack,
    ProviderList.MOCK: Mock
}

def get_cloud_provider(cloud):
    if cloud in cloud_constructors:
        return cloud_constructors.get(cloud)()
    print(f'Nothing provides {cloud} services')
    return None

END = '\033[0m'
BOLD = '\033[1m'

def bold(s):
    return BOLD + s + END

help_text = f'''{bold('SYNOPSIS')}
    Managed resources on any cloud infrastucture supported by Cloudbridge.
    
{bold('USAGE')}
    ./cloud.py <cloud> <resource> <command> [options]

{bold('CLOUDS')}
    The cloud infrastructure provider to use.  Authorizaion credentials must be
    specified in your ~/.cloudbridge file before you can use this script to
    manage resources on that cloud provided.  Supported providers are aws, gcp,
    and openstack.  The is also a mock provider available that can be used for
    debugging and testing.
    
{bold('RESOURCE')}
    {bold('- network')}
      {bold('- create <name>')}  Creates a network, subnet, router, gateway and 
        firewall (security group) using the given name.
      {bold('- delete <name>')} Deletes all network infrastructure for the given name.
      {bold('- list')}
    - keypair
      - create
      - delete
      - list 
    - instance
      - create
      - delete
      - list 
    - cluster
      Reserved for future use.
    - image
    - vm
        
{bold('NOTES')}

'''

def help():
    # print('python cloud.py [aws|gcp|openstack] [network|keypair|instance|cluster] [create|delete|list|help]')
    print(help_text)

class Parameters:
    def __init__(self):
        self.cloud = None
        self.resource = None
        self.command = None
        self.options = list()

    def is_valid(self):
        return not (self.resource is None or self.command is None or self.cloud is None)

    def parse(self, argv):
        self.parse_arg(argv[1])
        self.parse_arg(argv[2])
        self.parse_arg(argv[3])
        if not self.is_valid():
            print('Invalid command parameters')
            help()
            sys.exit(1)
        self.options = argv[4:]

    def parse_arg(self, arg):
        if arg in resources:
            self.resource = arg
        elif arg in commands:
            self.command = arg
        elif arg in clouds:
            self.cloud = arg
        else:
            print(f'Unexpected input {arg}')

    def print(self):
        print(f'Cloud   : {self.cloud}')
        print(f'Resource: {self.resource}')
        print(f'Command : {self.command}')
        print(f'Options : {self.options}')

if __name__ == "__main__":
    resource = None
    command = None
    cloud = None

    if len(sys.argv) == 1 or sys.argv[1] == 'help':
        help()
        sys.exit(1)

    params = Parameters()
    params.parse(sys.argv)
    if not params.is_valid():
        sys.exit(1)

    if params.resource not in handlers:
        print(f"{params.resource} not in handlers. This error should have been caught by now...")
        sys.exit(1)

    resource_handler = handlers.get(params.resource)
    if params.command not in resource_handler:
        print(f"{params.command} not in resource_handlers. This error should have been caught by now...")
        sys.exit(1)

    params.print()
    handler = resource_handler.get(params.command)
    cp = get_cloud_provider(params.cloud)
    if cp is None:
        print('WTF')
        sys.exit(1)
    handler(cp, params.options)


'''
cloud aws keypair create ks-galaxy-aws
cloud aws network create ks-testing-apr23
cloud aws instance create --keypair ks-galaxy-aws --name node-1 --vm m1.2xlarge
cloud aws instance list

network
- create <name>
- delete <name>
- list
keypair
- create <name>
- delete <name>
- list
instance
- create [-n|--name] <name> [-t|--type] <vm_type>
- delete [-n|--name] <name>
- list
cluster
- create [-n|--name] <name> [-s|--size] <num_nodes>
- delete [-n|--name] <name>
'''
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

def run(params):
    if params.cloud == ProviderList.AWS:
        cloud = AWS()
    elif params.cloud == ProviderList.GCP:
        cloud = GCP()
    elif params.cloud == ProviderList.OPENSTACK:
        cloud = OpenStack()
    else:
        print(f"Invalid cloud provider name {params.cloud}")
        return


def ignored():
    image_name = 'Ubuntu Server 20.04 LTS'
    # provider = CloudProviderFactory().create_provider(ProviderList.OPENSTACK, {})
    images = cloud.provider.compute.images.find(label=f'{image_name}*')
    print(cloud.image)
    # images = [ image for image in images if image.name == image_name]
    for image in images:
        print(f'ID   : {image.id}')
        print(f'Name : {image.name}')
        print(f'Label: {image.label}')
        print(f'Desc : {image.description}')
        print()

'''
def get_keypair():
    cloud = AWS()
    kp = cloud.get_keypair('ks-galaxy-aws')
    print(kp)


def create_network():
    cloud = AWS()
    cloud.initialize('foo')
    print("The cloud networking services have been initialized")


def delete_network():
    cloud = AWS()
    # cloud.initialize()
    cloud.tear_down(cloud_name)
    print("Cloud networking services have been deleted.")


def list_firewalls():
    cloud = AWS(cloud_name)
    firewalls = cloud.provider.security.vm_firewalls.list()
    print(f"Found {len(firewalls)} firewalls.")
    for fw in firewalls:
        print(f"{fw.id} {fw.label}")
    print()
    print('Cloud firewalls')
    for fw in cloud.firewalls():
        print(f'{fw.id} {fw.label}')
    if cloud.gateway is None:
        print("No gateway configured")
    else:
        print('\nFloating IPs')
        for ip in cloud.gateway.floating_ips.list():
            print(ip)
        print()
'''

