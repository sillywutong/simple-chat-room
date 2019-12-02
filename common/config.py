import json

with open('config.json') as setting_file:
    config = json.load(setting_file)

def get_config():
    return config
