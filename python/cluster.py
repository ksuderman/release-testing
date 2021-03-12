import yaml

class ClusterData:
    fields = ['network', 'subnet', 'router', 'firewall', 'instance', 'ip']

    def __init__(self, *args, **entries):
        if len(args) == 1:
            self.__dict__.update(yaml.safe_load(args[0]))
        else:
            self.__dict__.update(entries)

    def __repr__(self):
        return "ClusterData"

    def as_yaml(self):
        print("---")
        for item in self.__dict__ :
            if item is not None:
                print(f"{item}: {self.__dict__[item]}")


def cluster_representer(dumper, cluster):
    return dumper.represent_dict(cluster.__dict__.iteritems())

yaml.Dumper.add_representer(ClusterData, cluster_representer)

    # def __init__(self):
    #     self.network = None
    #     self.subnet = None
    #     self.router = None
    #     self.firewall = None
    #     self.instance = None

#     def as_yaml(self):
#         return f"""---
# network: {self.network.id}
# subnet: {self.subnet.id if self.subnet else 'None'}
# router: {self.router.id if self.router else 'None'}
# firewall: {self.firewall.id}
# instance: {self.instance.id}
# """
