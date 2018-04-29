#!/usr/bin/env python

import sys
sys.path.append('common')

from event import Event
from person import Person
from equipment_type import Equipment_type
import argparse
import configuration
import csv
import database
import yaml

def add_training(person, trainer, trained_date, equipment):
    if trainer:
        trainer = trainer._id
    event = Event.find('training', trained_date, [trainer], [equipment])
    person.add_event(event)

def import_main(verbose=True):
    # todo: convert all dates to datetime.datetime as mentioned in http://api.mongodb.com/python/current/examples/datetimes.html
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--equipment-types", default="equipment-types.csv")
    parser.add_argument("-e", "--equipment", default="equipment.csv")
    parser.add_argument("-m", "--members", default="members.csv")
    parser.add_argument("-u", "--users", default="users.csv")
    parser.add_argument("-o", "--owners", default="owners.csv")
    parser.add_argument("-t", "--trainers", default="trainers.csv")
    parser.add_argument("--delete-existing", action='store_true')
    parser.add_argument("-v", "--verbose", action='store_true')
    args = parser.parse_args()
    if args.verbose:
        verbose = True
    config = configuration.get_config()
    db_config = config['database']
    collection_names = db_config['collections']
    if verbose:
        print "collection names are", collection_names
    database.database_init(config, args.delete_existing)

    # todo: fix these
    # database[collection_names['people']].create_index('link_id')
    # database[collection_names['names']].create_index('link_id')


    if verbose:
        print "loading equipment types"
    with open(args.equipment_types) as types_file:
        for row in csv.DictReader(types_file):
            database.add_equipment_type(row['name'],
                                        row['training_category'],
                                        row['manufacturer'])

    if verbose:
        print "loading equipment"
    with open(args.equipment) as machines_file:
        for row in csv.DictReader(machines_file):
            database.add_machine(row['name'],
                                 row['equipment_type'],
                                 row['location'],
                                 row['acquired'])

    with open(args.members) as members_file:
        for row in csv.DictReader(members_file):
            name_parts = row['Name'].rsplit(" ", 1)
            member_no = row['Member no']
            database.add_person({'membership_number': member_no,
                                 'email': row['Email'],
                                 'given_name': name_parts[0],
                                 'surname': name_parts[1],
                                 'known_as': name_parts[0]},
                                {'membership_number': member_no,
                                 'training': database.create_timeline_id("training for " + name_parts[0] + " " + name_parts[1])})
            added = Person.find(row['Name'])
            if verbose:
                print "added person record", added
            inductor = Person.find(row['Inductor'])
            if verbose:
                print "inductor is", inductor
            inductor_id = inductor._id
            added.add_training(Event.find('training',
                                          row['Date inducted'],
                                          [inductor_id],
                                          [Equipment_type.find('makespace')._id]))
            inducted = Person.find(row['Name'])
            if verbose:
                print "inducted is", inducted, "with training", inducted.get_training_events()

    with open(args.users) as users_file:
        for row in csv.DictReader(users_file):
            person = Person.find(row['Name'])
            if person is None:
                print "Could not find", row['Name'], "to add training"
                continue
            trainer = Person.find(row['Trainer'])
            trainer_id = trainer._id if trainer else None
            person.add_training(Event.find('training',
                                           row['Date'],
                                           [trainer_id],
                                           [ Equipment_type.find(typename)._id
                                             for typename in row['Equipment'].split(';') ]))
            checkback = Person.find(row['Name'])
            if verbose:
                print "checkback is", checkback, "with training events", checkback.get_training_events()

if __name__ == "__main__":
    import_main()
