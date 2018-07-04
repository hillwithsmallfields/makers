#!/usr/bin/env python

from __future__ import print_function

import sys
sys.path.append('model')

from event import Event
from person import Person
from equipment_type import Equipment_type
import argparse
import configuration
import csv
import database
import yaml
import os

def import_template_file(file):
    if os.path.isdir(file):
        for f in os.listdir(file):
            import_template_file(os.path.join(file, f))
    else:
        with open(file, 'r') as confstream:
            incoming_template = yaml.load(confstream)
            if 'name' not in incoming_template:
                incoming_template['name'] = os.path.splitext(os.path.basename(file))[0]
            database.add_template(incoming_template)

def import_role_file(role, csv_file, verbose):
    with open(csv_file) as users_file:
        for row in csv.DictReader(users_file):
            tr_person = Person.find(row['Name'])
            if tr_person is None:
                print("Could not find", row['Name'], "to add training")
                continue
            trainer = Person.find(row.get('Trainer', "Joe Bloggs"))
            trainer_id = trainer._id if trainer else None
            equipment_type_names = row['Equipment'].split(';')
            equipment_type_ids = [ Equipment_type.find(typename)._id
                                   for typename in equipment_type_names ]
            if verbose:
                print("equipment", equipment_type_names, equipment_type_ids)
            training_event = Event.find(database.role_training(role),
                                        row['Date'],
                                        [trainer_id],
                                        equipment_type_ids)
            training_event.publish()
            training_event.add_invitation_accepted([tr_person])
            training_event.mark_results([tr_person], [], [])
            checkback = Person.find(row['Name'])
            if verbose:
                print("checkback is", checkback, "with training events", checkback.get_training_events())

def import_main(verbose=True):
    # todo: convert all dates to datetime.datetime as mentioned in http://api.mongodb.com/python/current/examples/datetimes.html
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--equipment-types", default="equipment-types.csv")
    parser.add_argument("-e", "--equipment", default="equipment.csv")
    parser.add_argument("-m", "--members", default="members.csv")
    parser.add_argument("-u", "--users", default="users.csv")
    parser.add_argument("-o", "--owners", default="owners.csv")
    parser.add_argument("-t", "--trainers", default="trainers.csv")
    parser.add_argument("-b", "--templates", default="event_templates")
    parser.add_argument("--delete-existing", action='store_true')
    parser.add_argument("-v", "--verbose", action='store_true')
    args = parser.parse_args()
    import0(args)

def import0(args):
    verbose = args.verbose
    config = configuration.get_config()
    db_config = config['database']
    collection_names = db_config['collections']
    if verbose:
        print("collection names are", collection_names)
    database.database_init(config, args.delete_existing)

    # todo: fix these
    # database[collection_names['people']].create_index('link_id')
    # database[collection_names['names']].create_index('link_id')
    # and so on for the other collections?

    if verbose:
        print("loading equipment types")
    with open(args.equipment_types) as types_file:
        for row in csv.DictReader(types_file):
            if verbose:
                print("Adding equipment type", row)
            database.add_equipment_type(row['name'],
                                        row['training_category'],
                                        row['manufacturer'])

    if verbose:
        print("loading equipment")
    with open(args.equipment) as machines_file:
        for row in csv.DictReader(machines_file):
            if verbose:
                print("Adding machine", row)
            database.add_machine(row['name'],
                                 Equipment_type.find(row['equipment_type'])._id,
                                 row['location'],
                                 row['acquired'])

    induction_event = None
    with open(args.members) as members_file:
        for row in csv.DictReader(members_file):
            name_parts = row['Name'].rsplit(" ", 1)
            member_no = row['Member no']
            database.add_person({'membership_number': member_no,
                                 'email': row['Email'],
                                 'given_name': name_parts[0],
                                 'surname': name_parts[1],
                                 'known_as': name_parts[0]},
                                {'membership_number': member_no})
            added = Person.find(row['Name'])
            added.set_fob(row.get('Fob', None))
            # todo: find or create a training event to match row['Date inducted']
            if verbose:
                print("added person record", added)
            inductor = Person.find(row['Inductor'])
            if verbose:
                print("inductor is", inductor)
            inductor_id = inductor._id
            # todo: record that the inductor is trained as an inducotr
            induction_event = Event.find('user_training',
                                          row['Date inducted'],
                                          [inductor_id],
                                          [Equipment_type.find(config['organization']['name'])._id])
            induction_event.add_invitation_accepted([added])
            induction_event.mark_results([added], [], [])
            # print("induction event is now", induction_event)
            added.add_training(induction_event)
            inducted = Person.find(row['Name'])
            if verbose:
                print("inducted is", inducted, "with training", inducted.get_training_events())

    import_role_file('owner', args.owners, verbose)
    # read the trainers before the people they train:
    import_role_file('trainer', args.trainers, verbose)
    import_role_file('user', args.users, verbose)
    import_template_file(args.templates)

if __name__ == "__main__":
    import_main()
