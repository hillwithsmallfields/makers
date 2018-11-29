#!/usr/bin/env python

from __future__ import print_function

import os
import sys
sys.path.append('model')
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from model.event import Event
from model.person import Person
from model.equipment_type import Equipment_type
import argparse
import model.configuration as configuration
import csv
import model.database as database
import yaml

def import_template_file(file):
    if file is not None and file != "None":
        if os.path.isdir(file):
            for f in os.listdir(file):
                import_template_file(os.path.join(file, f))
        else:
            with open(file, 'r') as confstream:
                incoming_template = yaml.load(confstream)
                if 'name' not in incoming_template:
                    incoming_template['name'] = os.path.splitext(os.path.basename(file))[0]
                print("adding template", incoming_template)
                database.save_event_template(incoming_template)

def import_role_file(role, csv_file, verbose):
    if csv_file is not None and csv_file != "None" :
        with open(csv_file) as users_file:
            for row in csv.DictReader(users_file):
                tr_person = Person.find(row['Name'])
                if tr_person is None:
                    print("Could not find", row['Name'], "to add training")
                    continue
                trainer = Person.find(row.get('Trainer', "Joe Bloggs"))
                trainer_id = trainer._id if trainer else None
                equipment_type_name = row['Equipment']
                equipment_type = Equipment_type.find(equipment_type_name)
                if equipment_type is None:
                    print("Could not find equipment type", equipment_type_name,
                          "and so skipping row", row, "of file", csv_file)
                    continue
                equipment_type_id = equipment_type._id
                if verbose:
                    print("equipment", equipment_type_name, equipment_type_id)
                training_event = Event.find(database.role_training(role),
                                            row['Date'],
                                            [trainer_id],
                                            equipment_type_id)
                training_event.publish()
                training_event.add_signed_up([tr_person])
                training_event.mark_results([tr_person], [], [])
                checkback = Person.find(row['Name'])
                if verbose:
                    print("checkback is", checkback, "with training events", checkback.get_training_events())

def import_main(verbose=True):
    # todo: convert all dates to datetime.datetime as mentioned in http://api.mongodb.com/python/current/examples/datetimes.html
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--equipment-types", default=None)
    parser.add_argument("-e", "--equipment", default=None)
    parser.add_argument("-m", "--members", default=None)
    parser.add_argument("-u", "--users", default=None)
    parser.add_argument("-o", "--owners", default=None)
    parser.add_argument("-t", "--trainers", default=None)
    parser.add_argument("-b", "--templates", default=None)
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
    database.database_init(config)

    if args.equipment_types is not None and args.equipment_types != "None":
        if verbose:
            print("loading equipment types")
        with open(args.equipment_types) as types_file:
            for row in csv.DictReader(types_file):
                if verbose:
                    print("Adding equipment type", row)
                database.add_equipment_type(row['name'],
                                            row['training_category'],
                                            row['manufacturer'])

    if args.equipment is not None and args.equipment != "None":
        if verbose:
            print("loading equipment")
        with open(args.equipment) as machines_file:
            for row in csv.DictReader(machines_file):
                eqty = Equipment_type.find(row['equipment_type'])
                if eqty is None:
                    print("Could not add machine", row, "as its type", row['equipment_type'], "could not be found")
                    continue
                if verbose:
                    print("Adding machine", row, "of type", eqty)
                database.add_machine(row['name'],
                                     eqty._id,
                                     row.get('location', "?"),
                                     row.get('acquired', "?"))

    if args.members is not None and args.members != "None":
        induction_event = None
        with open(args.members) as members_file:
            for row in csv.DictReader(members_file):
                # todo: check that they are not already in the collection
                name_parts = row['Name'].rsplit(" ", 1)
                member_no = row.get('Member no', "0")
                if member_no == "":
                    member_no = "0"
                database.add_person({'membership_number': int(member_no),
                                     'email': row.get('Email', None),
                                     'given_name': name_parts[0],
                                     'surname': name_parts[1],
                                     'known_as': name_parts[0],
                                     'admin_note': row.get('Note', None)},
                                    {'membership_number': member_no})
                added = Person.find(row['Name'])
                added.set_fob(row.get('Fob', None))
                # todo: find or create a training event to match row['Date inducted']
                if verbose:
                    print("added person record", added)
                # if no inductor, treat them as self-inducted, as was
                # presumably done while bootstrapping the induction
                # system:
                inductor = Person.find(row['Inductor']) or added
                if verbose:
                    print("inductor is", inductor)
                # todo: record that the inductor is trained as an inductor
                induction_event = Event.find('user_training',
                                              row['Date inducted'],
                                              [inductor._id],
                                              Equipment_type.find(config['organization']['name'])._id)
                induction_event.add_signed_up([added])
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
