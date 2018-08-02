#!/usr/bin/python

import os
import yaml

cached_config = None
cached_config_timestamp = 0

config_file_name = "/usr/local/share/makers/makers.yaml"

def get_config():
    """Read the config partly from file and perhaps some from the DB."""
    global cached_config, cached_config_timestamp
    file_timestamp = os.path.getmtime(config_file_name)
    if cached_config is None or file_timestamp > cached_config_timestamp:
        cached_config_timestamp = file_timestamp
        with open(config_file_name, 'r') as confstream:
            cached_config = yaml.load(confstream)
    return cached_config

def get_stylesheets():
    return sorted([css[:-4] for css in os.listdir(os.path.dirname(get_config()['page']['stylesheet']))
                   if css.endswith(".css")])
