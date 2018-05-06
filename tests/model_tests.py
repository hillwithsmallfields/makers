#!/usr/bin/python

import argparse
import json
import os
import sys
sys.path.append('common')
sys.path.append('utils')

import database
import importer
import person
import event
import equipment_type

def show_person(directory, person_object):
    old_stdout = sys.stdout
    name, known_as = database.person_name(person_object)
    sys.stdout = open(os.path.join(directory, name.replace(' ', '_') + ".txt"), 'w')
    print person_object
    print name, "known as", known_as
    print "Id", person_object._id
    training = person_object.get_training_events()
    print "training:"
    for session in training:
        print "  ", session
    all_remaining_types = set(equipment_type.Equipment_type.list_equipment_types())
    for role in ['user', 'trainer', 'owner']:
        their_equipment_types = set(person_object.get_equipment_classes(role))
        if len(their_equipment_types) > 0:
            print role, "of", [ ty for ty in their_equipment_types ]
            all_remaining_types -= their_equipment_types
    if len(all_remaining_types) > 0:
        print "Can sign up for training on", [ ty for ty in all_remaining_types ]

    # rethink this part
    print "can instantiate event templates", event.Event.list_templates([person_object], their_equipment_types)

    print "personal data for API:", json.dumps(person_object.api_personal_data(), indent=4)
    sys.stdout.close()
    sys.stdout = old_stdout

if __name__ == "__main__":
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
    print "importing from spreadsheet files"
    importer.import0(args)
    print "import complete, scanning list of people"
    for whoever in person.Person.list_all_people():
        show_person("user-pages", whoever)
    print "listing members"
    for whoever in person.Person.list_all_members():
        show_person("member-pages", whoever)
    print "Listing equipment types"
    all_types = equipment_type.Equipment_type.list_equipment_types()
    print "Equipment types are:", all_types
    for eqtype in all_types:
        old_stdout = sys.stdout
        sys.stdout = open(os.path.join("equipment-type-pages", eqtype.name.replace(' ', '_') + ".txt"), 'w')
        print "  users", [ user.name() for user in eqtype.get_trained_users() ]
        print "  owners",  [ user.name() for user in eqtype.get_owners() ]
        print "  trainers",  [ user.name() for user in eqtype.get_trainers() ]
        print "  enabled fobs", json.dumps(eqtype.API_enabled_fobs(), indent=4)
        sys.stdout.close()
        sys.stdout = old_stdout
    with open("allfobs.json", 'w') as outfile:
        outfile.write(json.dumps(equipment_type.Equipment_type.API_all_equipment_fobs(), indent=4))
