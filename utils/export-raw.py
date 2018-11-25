#!/usr/bin/env python

from __future__ import print_function

import os
import sys
sys.path.append('model')
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import argparse
import model.configuration as configuration
import csv
import model.database as database

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--collection", default='profiles')
    parser.add_argument("-o", "--output", default=None)
    args = parser.parse_args()
    config = configuration.get_config()
    db_config = config['database']
    collection_names = db_config['collections']
    database.database_init(config)
    collection = args.collection
    output_name = args.output or (collection + ".csv")
    rows = database.get_collection_rows(collection)
    keys = []
    for row in rows:
        for key in row.keys():
            if key not in keys:
                keys.push(key)
    print ("keys are", keys)
    with open(output_name, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, keys)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

if __name__ == "__main__":
    main()
