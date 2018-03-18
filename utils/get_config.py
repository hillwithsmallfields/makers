#!/usr/bin/python

import sys
sys.path.append('common')

import argparse
import config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    data = config.get_config()
    for step in args.path.split(':'):
        data = data[step]
    print step

if __name__ == "__main__":
    main()
