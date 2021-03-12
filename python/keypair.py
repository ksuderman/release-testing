import os
from provider import *
from settings import *
from cloudbridge.interfaces.exceptions import DuplicateResourceException

try:
    keyfile_path = keypair_name + ".pem"
    kp = provider.security.key_pairs.create(keypair_name)
    with open(keyfile_path, 'w') as f:
        f.write(kp.material)
        print(f"Wrote {keyfile_path}")
    os.chmod(keyfile_path, 0o400)
    print(kp)
except DuplicateResourceException as e:
    print("KeyPair already exists.")


