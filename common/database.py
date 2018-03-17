#!/usr/bin/python

import os
import json
import pymongo

client = None
database = None
people_collection = None
equipment_collection = None
events_collection = None

def database_init(config, delete_existing=False):
    global client, database, people_collection, equipment_collection, events_collection
    db_config = config['database']
    collection_names = db_config['collections']
    client = pymongo.MongoClient(db_config['URI'])
    database = client[db_config['database_name']]
    if delete_existing:
        database.drop_collection(collection_names['people'])
        database.drop_collection(collection_names['equipment'])
        database.drop_collection(collection_names['events'])
    people_collection = database[collection_names['people']]
    equipment_collection = database[collection_names['equipment']]
    events_collection = database[collection_names['events']]
    print "people_collection is", people_collection

def add_person(record):
    print "Adding person", record, "to collection", people_collection
    # todo: convert dates to datetime.datetime
    # todo: possibly use upsert
    people_collection.insert(record)

def members():
    """Return a list of all members."""


def get_person(name):
    """Read the data for a person from the database."""
    name_parts = name.rsplit(" ", 1)
    record = (people_collection.find_one({'given_name': name_parts[0],
                                         'surname': name_parts[1]})
              or people_collection.find_one({'email': name})
              or people_collection.find_one({'_id': name}))
    if record:
        return record
    return None

def get_machine(name):
    """Read the data for a machine from the database."""
    # todo: replace with mongodb stuff
    for machine in get_data()['equipment']:
        if (machine['name'] == name
            or machine['_id'] == name):
            return machine
    return None

def get_machine_class_people(machine_class, role):
    """For a given machine class, get a list of people in a given role.
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
