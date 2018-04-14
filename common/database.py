#!/usr/bin/python

import os
import json
import pymongo
import configuration

client = None
database = None
collection_names = None

def database_init(config, delete_existing=False):
    global client, database, collection_names
    db_config = config['database']
    collection_names = db_config['collections']
    print "collection names are", collection_names
    client = pymongo.MongoClient(db_config['URI'])
    database = client[db_config['database_name']]
    if delete_existing:
        # I think these are wrong
        database.drop_collection(collection_names['people'])
        database.drop_collection(collection_names['equipment'])
        database.drop_collection(collection_names['events'])

def get_person(name):
    """Read the data for a person from the database."""
    if isinstance(name, dict):
        return name             # no lookup needed
    name_parts = name.rsplit(" ", 1)
    collection = database[collection_names['people']]
    record = (collection.find_one({"surname" : name_parts[1], "given_name" : name_parts[0]})
              or collection.find_one({'email': name})
              or collection.find_one({'fob': name})
              or collection.find_one({'_id': name}))
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
    raw = database[collection_names['people']].find({role: machine_class})
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

def is_administrator(person, writer=False):
    """Return whether a person is an administrator who can access other people's data in the database.
    With the optional third argument non-False, check whether they have write access too."""
    return (configuration.get_config['organization']['database']
            in get_person_machines(person,
                                   'owner' if writer else 'trained'))

# You should generally use these functions to get these details of
# people, rather than looking directly in the relevant fields of the
# record, so that privacy protection can be applied.

def person_name(person, viewing_person):
    """Return the person's full name and nickname.
    If they have requested anonymity, only they and the admins can see their name."""
    person = get_person(person)
    viewing_person = get_person(viewing_person)
    if (person == viewing_person
        or not person.get("anonymized", False) # optional flag
        # todo: add an equipment arg to give context so that owners and trainers of that equipment can see this
        or is_administrator(viewing_person)):
        given_name = person['given_name']
        return given_name + " " + person['surname'], person.get('known_as', given_name)
    else:
        return "Anonymous", "Anon"

def person_email(person, viewing_person):
    """Return the person's email address.
    If they have requested anonymity, only they and the admins can see this."""
    return (person['email']
            if (person == viewing_person
                or not person.get("anonymized", False) # optional flag
                # todo: add an equipment arg to give context so that owners and trainers of that equipment can see this
                or is_administrator(viewing_person))
            else "anon@anonymous.com")

def add_person_machine_role(person, person_adding, machine_class, role):
    # todo: indicate that a person has a relationship to a machine class
    pass

def cancel_person_machine_role(person, person_cancelling, machine_class, role):
    # todo: indicate that a person no longer has a relationship to a machine class
    pass

def check_person_machine_role(person, machine_class, role):
    # todo: check whether a person has a relationship to a machine class
    return None

def add_person(record):
    # todo: convert dates to datetime.datetime
    # todo: possibly use upsert
    database[collection_names['people']].insert(record)
