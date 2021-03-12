from cloudbridge.factory import CloudProviderFactory
from cloudbridge.factory import ProviderList
from cloudbridge.providers.openstack.resources import OpenStackInternetGateway

provider = CloudProviderFactory().create_provider(ProviderList.OPENSTACK, {})

def get_gateway():
    gw_net = provider.neutron.list_networks(name='public').get('networks')[0]
    return OpenStackInternetGateway(provider, gw_net)
