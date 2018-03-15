#!/usr/bin/python

import sys
sys.path.append('../common')

import os
import json

loaded_data = None

def get_data():
    """Return the whole database.  For early debugging without a real db."""
    global loaded_data
    if loaded_data is None:
        # testing code follows
        file = os.path.expanduser("~/makers-data/data.json")
        if not os.path.exists(file):
            file = "/usr/local/share/makers-data.json"
        with open(file, 'r') as confstream:
            loaded_data = json.load(confstream)
    return loaded_data

def get_person(name):
    """Read the data for a person from the database."""
    data = get_data()
    # todo: replace with mongodb stuff
    for person in data['people']:
        if (person['email'] == name
            or person['_id'] == name
            or person['known_as'] == name):
            return person
    parts = name.split(' ')
    if len(parts) == 2:
        forename, surname = parts
        # todo: replace with mongodb stuff
        for person in data['people']:
            if person['family_name'] == surname and person['given_name'] == forename:
                return person
    return None

def get_machine(name):
    """Read the data for a machine from the database."""
    # todo: replace with mongodb stuff
    for machine in get_data()['equipment']:
        if (machine['name'] == name
            or machine['_id'] == name):
            return machine
    return None

def get_machine_people(machine, role):
    """For a given machine, get a list of people in a given role.
    The machine can be given by name or objectId.
    The role will be a list field of the machine document,
    typically 'trained', 'owner' or 'trainer'."""
    # todo: mongodb stuff
    return None

def get_person_machines(person, role):
    """Return the machines on which a person has a given role.
    The role will be a list field of the machine document,
    typically 'trained', 'owner' or 'trainer'."""
    # todo: mongodb stuff
    return None

def is_administrator(person):
    """Return whether a person is an administrator."""
    # todo: look up whether they are an owner of the database 'equipment'
    return False

def main():                     # for testing
    print get_person('jcg.sturdy@gmail.com')
    print get_person('John Sturdy')
    print get_machine("Betsy")

if __name__ == "__main__":
    main()
