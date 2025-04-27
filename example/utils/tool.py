import json


def load_config():
    import os;
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # config_path = os.path.join(current_dir, os.path.pardir)
    config_path = os.path.join(current_dir, os.path.pardir, "config.json")
    config=json.load(open(config_path, "r"))
    return config