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
    if file != "None":
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
    if csv_file != "None":
        with open(csv_file) as users_file:
            for row in csv.DictReader(users_file):
                tr_person = Person.find(row['Name'])
                if tr_person is None:
                    print("Could not find", row['Name'], "to add training")
                    continue
                trainer = Person.find(row.get('Trainer', "Joe Bloggs"))
                trainer_id = trainer._id if trainer else None
                equipment_type_name = row['Equipment']
                equipment_type_id = Equipment_type.find(equipment_type_name)._id
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
    database.database_init(config)

    # todo: fix these
    # database[collection_names['people']].create_index('link_id')
    # database[collection_names['profiles']].create_index('link_id')
    # and so on for the other collections?

    if args.equipment_types != "None":
        if verbose:
            print("loading equipment types")
        with open(args.equipment_types) as types_file:
            for row in csv.DictReader(types_file):
                if verbose:
                    print("Adding equipment type", row)
                database.add_equipment_type(row['name'],
                                            row['training_category'],
                                            row['manufacturer'])

    if args.equipment != "None":
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

    if args.members != "None":
        induction_event = None
        with open(args.members) as members_file:
            for row in csv.DictReader(members_file):
                name_parts = row['Name'].rsplit(" ", 1)
                member_no = row.get('Member no', "0")
                if member_no == "":
                    member_no = "0"
                database.add_person({'membership_number': int(member_no),
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
                inductor_id = inductor._id if inductor else None
                # todo: record that the inductor is trained as an inducotr
                induction_event = Event.find('user_training',
                                              row['Date inducted'],
                                              [inductor_id] if inductor_id else [],
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
