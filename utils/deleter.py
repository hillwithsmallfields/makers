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
    """Program to remove person entries completely.
    Originally meant for removing accidental duplicates."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--deletions",
                        help="""File containing the link_ids to delete, one per line""")
    parser.add_argument("-f", "--for-real",
                        action='store_true',
                        help="""Without this flag, only do a dummy run.""")
    args = parser.parse_args()
    for_real = args.for_real
    config = configuration.get_config()
    db_config = config['database']
    collection_names = db_config['collections']
    database.database_init(config)
    with open(args.deletions) as deletions_file:
        for del_link_id in deletions_file.readlines():
            if for_real:
                print("Deleting", del_link_id)
                print("Result:", database.delete_by_link_id(del_link_id))
            else:
                print("Would delete", del_link_id)
    print("Processed", count, "deletion records.")

if __name__ == "__main__":
    main()
