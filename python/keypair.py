import os
import argparse
from provider import *
from cloud.settings import *
from cloudbridge.interfaces.exceptions import DuplicateResourceException

def ignore():
    try:
        keyfile_path = AWS.keypair + ".pem"
        kp = provider.security.key_pairs.create(AWS.keypair)
        with open(keyfile_path, 'w') as f:
            f.write(kp.material)
            print(f"Wrote {keyfile_path}")
        os.chmod(keyfile_path, 0o400)
        print(kp)
    except DuplicateResourceException as e:
        print("KeyPair already exists.")


def run():
    pass


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Provisions a cluster on the specified Cloud infrastructure')
    # parser.add_argument('provider', metavar='CLOUD', type=str, nargs=1,
    #                     choices=['amazon', 'google', 'jetstream'],
    #                     help='The cloud provider to provision')
    # args = parser.parse_args('google')
    # run()
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('integers', metavar='N', type=int, nargs='+',
                        help='an integer for the accumulator')
    parser.add_argument('--sum', dest='accumulate', action='store_const',
                        const=sum, default=max,
                        help='sum the integers (default: find the max)')

    args = parser.parse_args()
    print(args.accumulate(args.integers))