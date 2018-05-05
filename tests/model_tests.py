#!/usr/bin/python

import argparse
import sys
sys.path.append('common')
sys.path.append('utils')

import database
import importer
import person
import event
import equipment_type

def show_person(person_object):
    print
    print person_object
    name, known_as = database.person_name(person_object)
    training = person_object.get_training_events()
    print name, "known as", known_as
    print "Id", person_object._id
    print "training:"
    for session in training:
        print "  ", session
    print "user of", person_object.get_equipment_classes('user')
    print "personal data for API", person_object.api_personal_data()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action='store_true')
    args = parser.parse_args()
    print "importing from spreadsheet files"
    importer.import_main(args.verbose)
    print "import complete, scanning list of people"
    for whoever in person.Person.list_all_people():
        show_person(whoever)
    print "list of members:"
    for whoever in person.Person.list_all_members():
        show_person(whoever)
    print "Equipment types:"
    for eqtype in equipment_type.Equipment_type.list_equipment_types():
        print "  ", eqtype
        print "  users", [ user.name() for user in eqtype.get_trained_users() ]
        print "  owners",  [ user.name() for user in eqtype.get_owners() ]
        print "  trainers",  [ user.name() for user in eqtype.get_trainers() ]
        print "  enabled fobs", eqtype.API_enabled_fobs()
    print "All equipment fobs:", equipment_type.Equipment_type.API_all_equipment_fobs()
