import os
import sys
import yaml
import logging
import cloudbridge
from cloudbridge.base.resources import BaseNetwork, BaseSubnet
from cloudbridge.factory import CloudProviderFactory
from cloudbridge.factory import ProviderList
from cloudbridge.interfaces.resources import TrafficDirection

# cloudbridge.set_stream_logger('CloudBridge', level=logging.INFO)
# log = logging.getLogger()

default_format_string = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
formatter = logging.Formatter(default_format_string)
HOME = os.environ.get('HOME')
CONF_DIR = os.path.join(HOME, '.cloud', 'config')

root = logging.getLogger()
if len(root.handlers) > 0:
    root.handlers[0].setFormatter(formatter)
else:
    fh = logging.StreamHandler()
    fh.setLevel(cloudbridge.TRACE)
    fh.setFormatter(formatter)
    root.addHandler(fh)

logger = logging.getLogger('CloudScript')
logger.setLevel(cloudbridge.TRACE)
# logger.handlers[0].setFormatter(formatter)


class CloudException(Exception):
    """Exceptions thrown in this module

    Attributes:
        message -- the reason for the exception
    """
    def __init__(self, message):
        self.message = message


def find(resource, label):
    logger.trace('Finding resource with label %s' % label)
    things = resource.find(label=label)
    if len(things) == 0:
        return None
    return things[0]


def init_network(cloud, cidr):
    logger.debug('Initializing the network %s' % cidr)
    network = find(cloud.provider.networking.networks, cloud.name)
    if network is None:
        logger.trace("Creating a new network")
        network = cloud.provider.networking.networks.create(label=cloud.name, cidr_block=cidr)
    else:
        logger.trace("Using the exiting network.")
    if network is None:
        logger.critical('Unable to initialize the network')
        raise CloudException(f"Unable to provision the network for {cloud.name}.")
    else:
        logger.trace('Created a network')
    cloud.network = network
    if cloud.gateway is None:
        cloud.gateway = network.gateways.get_or_create()
        print(f'Attached gateway {cloud.gateway.id}')
    logger.debug("Network initialized")


def init_subnet(cloud, cidr):
    logger.debug("Initializing the subnet %s" % cidr)
    label = cloud.name + '-subnet'
    subnet = find(cloud.network.subnets, label)
    if subnet is None:
        subnet = cloud.network.subnets.create(label=label, cidr_block=cidr)
    else:
        logger.trace('Using the existing subnet')
    if subnet is None:
        raise CloudException(f"Unable to provision the subnet for {cloud.name}")
    else:
        logger.trace('Created a subnet')
    cloud.subnet = subnet
    logger.debug('Subnet initialized')


def init_firewall(cloud):
    logger.debug("Initializing the firewall")
    walls = cloud.provider.security.vm_firewalls.find(label=cloud.name)
    if walls is None or len(walls) == 0:
        fw = cloud.provider.security.vm_firewalls.create(
            label=cloud.name, description="Firewall rules for Keith's test networks",
            network=cloud.network)
        fw.rules.create(TrafficDirection.INBOUND, 'tcp', 22, 22, '0.0.0.0/0')
        fw.rules.create(TrafficDirection.INBOUND, 'tcp', 443, 443, '0.0.0.0/0')
        fw.rules.create(TrafficDirection.INBOUND, 'tcp', 4430, 4430, '0.0.0.0/0')
        fw.rules.create(TrafficDirection.INBOUND, 'tcp', 80, 80, '0.0.0.0/0')
        fw.rules.create(TrafficDirection.INBOUND, 'tcp', 8080, 8080, '0.0.0.0/0')
        cloud.firewall = fw
        logger.trace('Firewall created')
    else:
        cloud.firewall = walls[0]
        logger.trace('Using the existing firewall')
    logger.debug('Firewall initialized')


def init_router(cloud):
    logger.debug('Initializing the router')
    router = find(cloud.provider.networking.routers, cloud.name)
    if router is None:
        router = cloud.provider.networking.routers.create(network=cloud.network, label=cloud.name)
    if router is None:
        raise CloudException(f'Unable to initialize the router for {cloud.name}')
    router.attach_subnet(cloud.subnet)
    cloud.router = router
    logger.debug('Router initialized')

class Cloud:
    def __init__(self, provider, config={}):
        self.provider = CloudProviderFactory().create_provider(provider, config)
        self.name = None
        self.keypair = None
        self.network = None
        self.subnet = None
        self.router = None
        self.gateway = None
        self.firewall = None
        self.instances = list()
        conf_dir = os.path.join(os.environ.get('HOME'), '.cloud')
        self.auth_dir = os.path.join(conf_dir, 'auth')
        self.conf_dir = os.path.join(conf_dir, 'config')
        self.cluster_dir = os.path.join(conf_dir, 'clusters')

    def initialize(self, name, net_cidr=BaseNetwork.CB_DEFAULT_IPV4RANGE, subnet_cidr=BaseSubnet.CB_DEFAULT_SUBNET_IPV4RANGE):
        self.name = name
        dir = os.path.join(self.cluster_dir, name)
        conf_path = os.path.join(dir, self.conf_file)
        if os.path.exists(conf_path):
            print('A network with that name already exists.')
            return

        logger.info("Initializing cloud %s" % self.name)
        init_network(self, net_cidr)
        init_subnet(self, subnet_cidr)
        init_router(self)
        init_firewall(self)
        data = {
            'network': self.network.id,
            'subnet': self.subnet.id,
            'router': self.router.id,
            'firewall': self.firewall.id,
            'gateway': self.gateway.id
        }

        if not os.path.exists(dir):
            os.mkdir(dir)
            if not os.path.exists(dir):
                print(f'Unable to create directory {dir}')
                return

        with open(conf_path, 'w') as f:
            yaml.safe_dump(data, f)
            print(f'Wrote {conf_path}')
        logger.info("Cloud network infrastructure initialized")


    def safe_delete(self, resource):
        if resource is None:
            return
        # try:
            # print(f'Deleting resource {resource.id}')
            resource.delete()
        # except:
        #     print("Unexpected error deleting resource:", sys.exc_info()[0])


    def get_networking_metadata(self, name):
        network = find(self.provider.networking.networks, name)
        subnet = None
        if network is not None:
            subnet = find(network.subnets, name + '-subnet')
        router = find(self.provider.networking.routers, name)
        return {
            'network': network.id if network else 'Undefined',
            'subnet': subnet.id if subnet else 'Undefined',
            'router': router.id if router else 'Undefined'
        }


    def tear_down_from_file(self, config):
        with open(config) as f:
            print(f'Loading {config}')
            data = yaml.safe_load(f)

        fw_id = data['firewall']
        fw = self.provider.security.vm_firewalls.get(fw_id)
        if fw is not None:
            fw.delete()
            logger.info('Deleted the firewall %s', fw.id)

        network = self.provider.networking.networks.get(data['network'])
        router = self.provider.networking.routers.get(data['router'])
        if network:
            for subnet in network.subnets:
                logger.info('Deleting subnet %s' % subnet.id)
                if router:
                    router.detach_subnet(subnet)
                subnet.delete()
            for gw in network.gateways:
                logger.info("Deleting gateway %s" % gw)
                if router:
                    router.detach_gateway(gw)
                gw.delete()
        if router is not None:
            logger.info('Deleting the router %s' % router.id)
            router.delete()

        if network is not None:
            logger.info('Deleting the network %s' % network.id)
            network.delete()
        print(f"Removing config {config}")
        os.remove(config)

    def tear_down(self, name):
        logger.info('Tearing down cloud network infrastructure for %s' % name)
        config = os.path.join(self.cluster_dir, name, self.conf_file)
        if os.path.exists(config):
            self.tear_down_from_file(config)
            return

        walls = self.provider.security.vm_firewalls.find(label=name)
        if walls is not None and len(walls) > 0:
            for fw in walls:
                logger.info(f"Removing security group {fw}")
                fw.delete()

        network = None
        subnet = None
        nets = self.provider.networking.networks.find(label=name)
        if nets is not None and len(nets) > 0:
            logger.debug("Found the network")
            network = nets[0]
            subs = network.subnets.find(label=f'{name}-subnet')
            if subs is not None and len(subs) > 0:
                subnet = subs[0]
        objs = self.provider.networking.routers.find(label=name)
        if objs is not None and len(objs) > 0:
            router = objs[0]
            if subnet is not None:
                print("Detaching subnet from router")
                router.detach_subnet(subnet)
            router.delete()
            print("Router deleted")
        else:
            print("Router not found")

        if subnet is not None:
            subnet.delete()
            print("Subnet deleted")
        else:
            print('Subnet not found')

        if network is not None:
            for gw in network.gateways.list():
                print(f'Removing gateway {gw.id}')
                gw.delete()
            network.delete()
            print('Network deleted')
        else:
            print("Network not found")


        # inst.delete()
        # if self.router is not None:
        #     if self.gateway is not None:
        #         self.router.detach_gateway(self.gateway)
        #     if self.subnet is not None:
        #         self.router.detach_subnet(self.subnet)
        #
        # for resource in [self.firewall, self.gateway, self.router, self.subnet, self.network]:
        #     self.safe_delete(resource)
        # self.firewall.delete()
        # self.gateway.delete()
        # self.router.delete()
        # self.subnet.delete()
        # self.network.delete()
        logger.info('Tear down complete')

    def firewalls(self):
        return self.provider.security.vm_firewalls.find(label=self.name)

    def create_instance(self, name, keypair, cluster):
        # if self.network is None:
        #     logger.warning(f'Please provision the network before attempting to launch instances')
        #     return
        config = os.path.join(self.cluster_dir, cluster, self.conf_file)
        if not os.path.exists(config):
            logger.error(f'No configuration found for {config}')
            return

        with open(config, 'r') as f:
            data = yaml.safe_load(f)

        fw = self.provider.security.vm_firewalls.get(data['firewall'])
        if fw is None:
            logger.error('Unable to locate the firewall')
            return
        network = self.provider.networking.networks.get(data['network'])
        subnet = network.subnets.get(data['subnet'])
        kp = self.provider.security.key_pairs.get(keypair)
        if kp is None:
            logger.error('No such keypair: %s' % keypair)
            return

        logger.info('Creating instance %s', name)
        instance = self.provider.compute.instances.create(
            image=self.image, vm_type=self.vm, label=cluster + "-" + name,
            subnet=subnet, key_pair=kp, vm_firewalls=[fw])

        # print(instance)
        # Wait until ready
        logger.debug('Waiting for the instance to come up.')
        instance.wait_till_ready()  # This is a blocking call
        if not instance.public_ips:
            igw = network.gateways.get_or_create()
            # fip = self.gateway.floating_ips.create()
            fip = igw.floating_ips.create()
            instance.add_floating_ip(fip)
            instance.refresh()
            logger.info('Assigned Floating IP %s' % fip)

        logger.info('Instance created')
        return instance

    def delete_instance(self, name):
        instances = self.provider.compute.instances.find(label=name)
        if instances is None or len(instances) == 0:
            print("No such instance found.")
            return
        if len(instances) == 1:
            print(f'Deleting instance {instances[0].id}')
            instances[0].delete()
        else:
            print('Found the following instances')
            for instance in instances:
                print(f'    {instance.id}')
            print()

    def get_keypair(self, name=None):
        if name is None:
            name = self.name
        logger.debug('Getting keypair %s' % name)
        kp = self.provider.security.key_pairs.get(name)
        if kp is None:
            logger.debug('Creating a new keypair')
            keyfile_path = self._get_keyfile_path(name + '.pem')
            if keyfile_path is None:
                print(f"A key with that name already exists: {name + '.pem.'}")
                return None
            kp = self.provider.security.key_pairs.create(name)
            with open(keyfile_path, 'w') as f:
                f.write(kp.material)
                logger.info(f"Wrote {keyfile_path}")
            os.chmod(keyfile_path, 0o400)
        else:
            logger.debug('Using an existing keypair')
        self.keypair = kp
        return kp

    def _get_keyfile_path(self, filename):
        home = os.getenv('HOME')
        path = os.path.join(home, '.ssh', filename)
        if os.path.exists(path):
            return None
        return path

    def load_config(self):
        # path = f'~/.cloudbridge/{filename}'
        path = os.path.join(self.conf_dir, self.name + 'yml')
        if not os.path.exists(path):
            data = {
                'image': self.image,
                'vm': self.vm
            }
            with open(path, 'w') as f:
                yaml.safe_dump(data, f)
            print(f'Wrote configuration {path}')
        else:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                self.image = data.get('image')
                self.vm = data.get('vm')

    def save_config(self):
        data = {
            'image': self.image,
            'vm': self.vm
        }
        path = os.path.join(self.conf_dir, self.name + 'yml')
        with open(path, 'w') as f:
            yaml.safe_dump(data, f)
            print(f'Wrote {path}')


class OpenStack(Cloud):
    def __init__(self, config={}):
        super().__init__(ProviderList.OPENSTACK, config)
        self.image = '46794408-6a80-44b1-bf5a-405127753f43'
        self.vm = 'm1.medium'
        self.name = 'openstack'
        self.load_config()


class AWS(Cloud):
    def __init__(self, config={}):
        super().__init__(ProviderList.AWS, config)
        self.image = 'ami-042e8287309f5df03' # 'ami-0bb4f114a1e805434'
        self.vm = 't2.2xlarge'
        self.name = 'aws'
        self.load_config()


class GCP(Cloud):
    def __init__(self, config={}):
        super().__init__(ProviderList.GCP, config)
        self.image = None
        self.vm = None
        self.name = 'gcp'
        self.load_config()


class Mock(Cloud):
    def __init__(self, config={}):
        super().__init__(ProviderList.MOCK, config)
        self.image = None
        self.vm = None
        self.name = 'mock'