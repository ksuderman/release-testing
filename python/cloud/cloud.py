#!/usr/bin/env python

import argparse
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
    parser = argparse.ArgumentParser(description='Delete a keypair from the cloud provider', prog=f'{sys.argv[0]} <cloud> keypair delete')
    parser.add_argument('-f', '--force', action='store_true', help='delete the remote keypair even if we do not have a copy of the private key')
    parser.add_argument('name', type=str, help='the name of the keypair to delete')
    args = parser.parse_args(options)

    # if len(options) != 1:
    #     print("ERROR: keypair delete expects one parameter, the name of the keypair to delete.")
    #     return
    home = os.environ.get('HOME')
    path = os.path.join(home, '.ssh', args.name + '.pem')
    if os.path.exists(path):
        os.remove(path)
        print(f'Deleted local key file {path}')
    elif not args.force:
        print(f'No local key found. Refusing to delete remote keypair!')
        return

    cloud.provider.security.key_pairs.delete(args.name)
    print(f'Deleted keypair {args.name}')


def keypair_list(cloud, options):
    print(cloud)
    print("Keypairs:")
    for kp in cloud.provider.security.key_pairs.list():
        print(kp)


def instance_create(cloud, options):
    parser = argparse.ArgumentParser(description='Provision a new instance.', prog=f'{sys.argv[0]} <cloud> instance create')
    parser.add_argument('-k', '--keypair', help='the keypair to use for the instance', required=True)
    parser.add_argument('-c', '--network', help='the name of the cluster the instance will be assigned to', required=True)
    parser.add_argument('-n', '--name', help='a name for the instance.', required=True)
    args = parser.parse_args(options)
    cloud.create_instance(name=args.name, kp_name=args.keypair, cluster=args.network)


def instance_delete(cloud, options):
    # parser = argparse.ArgumentParser(description='Delete an instance.', prog=f'{sys.argv[0]} <cloud> instance delete')
    # parser.add_argument('-c', '--cluster', dest='cluster', help='the name of the cluster containing the instance', required=True)
    # parser.add_argument('-n', '--name', dest='name', help='a name for the instance.', required=True)
    # args = parser.parse_args(options)
    # name = args.cluster + '-' + args.name
    if len(options) != 1:
        print('ERROR: instance delete requires exactly one parameter, the name of the instance to delete.')
        return
    # print(f'Deleting instance {options[0]}')
    cloud.delete_instance(name=options[0])


def instance_list(cloud, options):
    # print("instance_list")
    print('Instances:')
    for instance in cloud.provider.compute.instances.list():
        print(f'    {instance.id} - {instance.label : >}')
    print()

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

# Used to validate command line parameters.
resources = [ 'network', 'keypair', 'instance', 'cluster', 'image', 'vm']
commands = [ 'create', 'delete', 'list', 'set', 'get', 'help' ]
clouds = [ProviderList.AWS, ProviderList.GCP, ProviderList.OPENSTACK, ProviderList.MOCK, 'os']

# Map the command line parameter to an object constructor.
cloud_constructors = {
    ProviderList.AWS: AWS,
    ProviderList.GCP: GCP,
    ProviderList.OPENSTACK: OpenStack,
    ProviderList.MOCK: Mock,
    'os': OpenStack
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


help_text = f'''
{bold('SYNOPSIS')}
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
    - {bold('network')}
      - {bold('create <name>')}  Creates a network, subnet, router, gateway and 
            firewall (security group) using the given name.
      - {bold('delete <name>')} Deletes all network infrastructure for the given name.
      - {bold('list')} List all configured networks
    - {bold ('keypair')}
      - {bold('create <name>')} Generates a new keypair.  The private key will 
            be downloaded to your ~/.ssh directory. This is the only time you 
            will be able to download the private key. 
      - {bold('delete <name>')} Deletes a keypair from the server and the 
            local private key in ~/.ssh. Once a keypair has been deleted any 
            instances configured to use that keypair will be unaccessible.
      - {bold('list')} Lists a keypairs available.
    - {bold('instance')}
      - {bold('create [-k|--key-pair] key.pem [-n|--name] <name>')} provisions 
            a new server instance.
      - {bold('delete <name>')} Decommisions a running instance.
      - {bold('list')} Lists all running instances
    - {bold('cluster')}
          Reserved for future use.
    - {bold('image')}
      - {bold('get')} Displays the image ID that will be used to provision
            instances.
      - {bold('set <image id>')} Set the image ID to be used to provision
            instances.
    - {bold('vm')}
      - {bold('get')}  Displays the VM type that will be used to provision
            instances.
      - {bold('set <vm type>')} Set the VM type that will be used to provision
            instances.
        
{bold('EXAMPLES')}

    {bold('$>')} ./cloud.py aws network create my-network        
    {bold('$>')} ./cloud.py openstack network create my-network
    {bold('$>')} ./cloud.py gcp keypair create my-keypair
    {bold('$>')} ./cloud.py openstack vm set m1.xlarge        
        
{bold('NOTES')}

    The first three parameters; cloud, resource, and command, can be specified
    in any order.  That is, the following commands are all functionally 
    equivalent:
    
    {bold('$>')} ./cloud.py aws network create my-network
    {bold('$>')} ./cloud.py create aws network my-network
    {bold('$>')} ./cloud.py network create aws my-network
    
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

    handler = resource_handler.get(params.command)
    cp = get_cloud_provider(params.cloud)
    if cp is None:
        print(f'Cloud provider not found: {params.cloud}')
        sys.exit(1)
    handler(cp, params.options)


'''
These are just some notes regarding what the commands _should_ look like.

cloud aws keypair create ks-galaxy-aws
cloud aws network create ks-testing-apr23
cloud aws instance create --keypair ks-galaxy-aws --name node-1
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
