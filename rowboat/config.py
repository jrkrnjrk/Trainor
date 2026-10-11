import yaml

with open('config.yaml', 'r') as f:
    loaded = yaml.safe_load(f.read())
    if loaded:
        locals().update(loaded)
