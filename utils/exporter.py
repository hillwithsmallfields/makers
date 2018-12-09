#!/usr/bin/env python

from __future__ import print_function

import os
import sys
sys.path.append('model')
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import model.backup_to_csv
from model.event import Event
from model.person import Person
from model.equipment_type import Equipment_type
import argparse
import model.configuration as configuration
import csv
import model.database as database
import yaml

def export_role(role, csv_file):
    with open(csv_file, 'w') as role_stream:
        eqtys = Equipment_type.list_equipment_types()
        rows = []
        for eqty in eqtys:
            print("getting eqty", eqty)
            rows += eqty.backup_API_people(role)
        writer = csv.DictWriter(role_stream,
                                ['Equipment', 'Name', 'Date', 'Trainer'],
                                extrasaction='ignore')
        writer.writeheader()
        for row in rows:
           writer.writerow(row)

def export_main(verbose=True):
    # todo: convert all dates to datetime.datetime as mentioned in http://api.mongodb.com/python/current/examples/datetimes.html
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--all", default=None)
    # parser.add_argument("-y", "--equipment-types", default=None)
    # parser.add_argument("-e", "--equipment", default=None)
    # parser.add_argument("-m", "--members", default=None)
    parser.add_argument("-u", "--users", default=None)
    # parser.add_argument("-o", "--owners", default=None)
    # parser.add_argument("-t", "--trainers", default=None)
    # parser.add_argument("-b", "--templates", default=None)
    parser.add_argument("-v", "--verbose", action='store_true')
    args = parser.parse_args()
    export0(args)

def export0(args):
    verbose = args.verbose
    config = configuration.get_config()
    db_config = config['database']
    collection_names = db_config['collections']
    if verbose:
        print("collection names are", collection_names)
    database.database_init(config)
    if args.all:
        model.backup_to_csv.make_database_backup(args.all)
    if args.users:
        export_role('user', args.users)

if __name__ == "__main__":
    export_main()
