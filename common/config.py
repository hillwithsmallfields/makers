#!/usr/bin/python

import sys
sys.path.append('../common')

import os
import yaml

def get_config():
    """Read the config partly from file and perhaps some from the DB."""
    file = os.path.expanduser("~/makers-bin/makers.yaml")
    if not os.path.exists(file):
        file = "/usr/local/share/makers.yaml"
    with open(file, 'r') as confstream:
        return yaml.load(confstream)

def main():                     # for testing
    print get_config()

if __name__ == "__main__":
    main()
