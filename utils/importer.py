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
import os

def add_training(person, trainer, trained_date, equipment):
    if trainer:
        trainer = trainer._id
    event = Event.find('training', trained_date, [trainer], [equipment])
    person.add_training(event)
    person.attendees.append(person._id)
    person.passed.append(person._id)

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
            person = Person.find(row['Name'])
            if person is None:
                print "Could not find", row['Name'], "to add training"
                continue
            trainer = Person.find(row.get('Trainer', "Joe Bloggs"))
            trainer_id = trainer._id if trainer else None
            # todo: record that the trainer is trained as a trainer --- maybe read the trainers list first
            equipment_type_names = row['Equipment'].split(';')
            equipment_type_ids = [ Equipment_type.find(typename)._id
                                   for typename in equipment_type_names ]
            if verbose:
                print "equipment", equipment_type_names, equipment_type_ids
            training_event = Event.find(database.role_training(role),
                                        row['Date'],
                                        [trainer_id],
                                        equipment_type_ids)
            training_event.add_attendees([person])
            training_event.mark_results([person], [], [])
            person.add_training(training_event)
            checkback = Person.find(row['Name'])
            if verbose:
                print "checkback is", checkback, "with training events", checkback.get_training_events()

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
                                {'membership_number': member_no})
            added = Person.find(row['Name'])
            added.set_fob(row.get('Fob', None))
            if verbose:
                print "added person record", added
            inductor = Person.find(row['Inductor'])
            if verbose:
                print "inductor is", inductor
            inductor_id = inductor._id
            # todo: record that the inductor is trained as an inducotr
            induction_event = Event.find('user_training',
                                          row['Date inducted'],
                                          [inductor_id],
                                          [Equipment_type.find(config['organization']['name'])._id])
            induction_event.add_attendees([added])
            induction_event.mark_results([added], [], [])
            added.add_training(induction_event)
            inducted = Person.find(row['Name'])
            if verbose:
                print "inducted is", inducted, "with training", inducted.get_training_events()

    import_role_file('owner', args.owners, verbose)
    import_role_file('trainer', args.trainers, verbose)
    import_role_file('user', args.users, verbose)
    import_template_file(args.templates)

if __name__ == "__main__":
    import_main()
