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
    return [ person for person in people_collection.find({}) ]

def get_person(name):
    """Read the data for a person from the database."""
    print "get_person", name
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
    # todo: make this find a <role> which has an entry with the appropriate machine_class
    raw = people_collection.find({role: machine_class})
    checked = {}
    # todo: filter the ones which have been cancelled
    return None

def get_person_machines(person, role):
    """Return the machines on which a person has a given role.
    The role will be a list field of the machine document, typically
    'trained', 'owner' or 'trainer'.  The result will be a dictionary
    keyed by equipment class, with the values in the result being
    dictionaries giving their name, the equipment class, when they
    were trained and who by."""
    if isinstance(person, basestring):
        person = get_person(person)
    if role not in person:
        return None
    latest_periods = person[role]
    enablements = {}
    for record in latest_periods:
        if (record['equipment_class'] not in enablements
            and record.get('until', None) is None):
            enablements[record['equipment_class']] = record
    return enablements

def is_administrator(person, config, writer=False):
    """Return whether a person is an administrator who can access other people's data in the database.
    With the optional third argument non-False, check whether they have write access too."""
    return (config['organization']['database']
            in get_person_machines(person,
                                   'owner' if writer else 'trained'))

def add_person_machine_role(person, person_adding, machine_class, role):
    # todo: indicate that a person has a relationship to a machine class
    pass

def cancel_person_machine_role(person, person_cancelling, machine_class, role):
    # todo: indicate that a person no longer has a relationship to a machine class
    pass


def check_person_machine_role(person, machine_class, role):
    # todo: check whether a person has a relationship to a machine class
    return None

def main():                     # for testing
    print get_person('jcg.sturdy@gmail.com')
    print get_person('John Sturdy')
    print get_machine("Betsy")

if __name__ == "__main__":
    main()
