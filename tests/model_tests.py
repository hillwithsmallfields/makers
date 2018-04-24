#!/usr/bin/python

import sys
sys.path.append('common')
sys.path.append('utils')

import database
import importer
import person

def show_person(person):
    print
    print person
    name, known_as = database.person_name(person)
    training = person_object.get_training()
    print name, "known as", known_as
    print "training:", training

if __name__ == "__main__":
    importer.import_main(False)
    for person in person.all_people():
        show_person(person)
