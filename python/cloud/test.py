from settings import AWS

def run():
    cloud = AWS()
    nets = cloud.provider.networking.networks.find(label='ks-testing-0424')
    if nets is not None and len(nets) > 0:
        net = nets[0]
        print(net.id, net.label)
        for gw in net.gateways.list():
            print(gw)
            gw.delete()
        net.delete()
        print('deleted network')
    else:
        print('No network found with that name')
if __name__ == '__main__':
    run()