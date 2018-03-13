#!/usr/bin/python

import sys
sys.path.append('../common')

import os
import json

loaded_data = None

def get_data():
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
    for person in data['people']:
        if (person['email'] == name
            or person['known_as'] == name):
            return person
    parts = name.split(' ')
    if len(parts) == 2:
        forename, surname = parts
        for person in data['people']:
            if person['family_name'] == surname and person['given_name'] == forename:
                return person
    return None

def get_machine(name):
    for machine in get_data()['equipment']:
        if machine['name'] == name:
            return machine
    return None

def main():                     # for testing
    print get_person('jcg.sturdy@gmail.com')
    print get_person('John Sturdy')
    print get_machine("Betsy")

if __name__ == "__main__":
    main()
