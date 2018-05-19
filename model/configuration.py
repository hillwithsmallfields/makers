#!/usr/bin/python

import os
import yaml

cached_config = None

def get_config():
    """Read the config partly from file and perhaps some from the DB."""
    global cached_config
    if cached_config is None:
        file = os.path.expanduser("~/makers-data/makers.yaml")
        if not os.path.exists(file):
            file = "/usr/local/share/makers/makers.yaml"
        with open(file, 'r') as confstream:
            cached_config = yaml.load(confstream)
    return cached_config
