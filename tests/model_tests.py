#!/usr/bin/python

import argparse
import sys
sys.path.append('common')
sys.path.append('utils')

import database
import importer
import person
import event

def show_person(person_object):
    print
    print person
    name, known_as = database.person_name(person_object)
    training = person_object.get_training_events()
    print name, "known as", known_as
    print "Id", person._id
    print "training:"
    for session in training:
        print "  ", session
    print "user of", person.get_equipment_classes('user')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action='store_true')
    args = parser.parse_args()
    print "importing from spreadsheet files"
    importer.import_main(args.verbose)
    print "import complete, scanning list of people"
    for person in person.all_people():
        show_person(person)
