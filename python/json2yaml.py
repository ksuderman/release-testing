import os
import json
import yaml

def run():
    home = os.getenv('HOME')
    with open(f'{home}/.secret/AnVIL.json') as f:
        config = json.load(f)

    yaml_config = yaml.safe_dump(config)
    out_path = f'{home}/.clouds/gcp.yml'
    with open(out_path, 'w') as f:
        f.write(yaml_config)
        print(f"Wrote {out_path}")


if __name__ == '__main__':
    run()