#!/usr/bin/python

import sys
sys.path.append('common')
sys.path.append('utils')

import database
import importer
import person

def show_person(person_object):
    print
    print person
    name, known_as = database.person_name(person_object)
    training = person_object.get_training_events()
    print name, "known as", known_as
    print "training:", training

if __name__ == "__main__":
    print "importing from spreadsheet files"
    importer.import_main(False)
    print "import complete, scanning list of people"
    for person in person.all_people():
        show_person(person)
