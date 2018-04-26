#!/usr/bin/python

import configuration
import event
import json
import os
import person
import pymongo
import uuid

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

def get_person_dict(identification):
    """Read the data for a person from the database, as a dictionary."""
    if isinstance(identification, dict):
        return identification             # no lookup needed
    if isinstance(identification, person.Person):
        return identification.__dict__
    collection = database[collection_names['people']]
    return (collection.find_one({'_id': identification})
            or collection.find_one({'link_id': identification})
            or collection.find_one({'fob': identification})
            # names and email addresses are kept in a separate database
            or collection.find_one({'link_id': name_to_id(identification)}))

def person_name(whoever):
    """Return the formal and informal names of a person, or not, if they're anonymous.
    Always use this to get someone's name; this way, anonymity is handled for you."""
    # todo: add admin override of anonymity
    person_link = (whoever['link_id']
                   if isinstance(whoever, dict)
                   else (whoever.link_id
                         if isinstance(whoever, person.Person)
                         else whoever))
    name_record = database[collection_names['names']].find_one({'link_id': person_link})
    if name_record is None:
        return "unknown", "unknown"
    if name_record.get('anonymous', False):
        if 'membership_number' in name_record:
            num_string = str(name_record['membership_number'])
            return "member " + num_string, num_string
        else:
            return "Anonymous member", "Anon"
    else:
        return (name_record.get('given_name', "?") + " " + name_record.get('surname', "?"),
                name_record.get('known_as', name_record.get('given_name', "?")))

def name_to_id(name):
    name_parts = name.rsplit(" ", 1)
    collection = database[collection_names['names']]
    record = (collection.find_one({"surname" : name_parts[-1], "given_name" : name_parts[0]})
              if len(name_parts) >= 2
              else (collection.find_one({"known_as" : name})
                    or collection.find_one({"email" : name})))
    return record and record.get('link_id', None)

def add_person(name_record, main_record):
    # todo: convert dates to datetime.datetime
    linking_id = str(uuid.uuid4())
    main_record['link_id'] = linking_id # todo: make it index by this
    name_record['link_id'] = linking_id # todo: make it index by this
    database[collection_names['people']].insert(main_record)
    database[collection_names['names']].insert(name_record)

def get_machine(name):
    """Read the data for a machine from the database."""
    collection = database[collection_names['equipment']]
    return (collection.find_one({'name': name})
            or collection.find_one({'_id': name}))

def get_event(event_type, event_datetime, hosts, equipment, create=True):
    """Read the data for an event from the database."""
    # print "Looking for event", "hosts,", hosts, "date", event_datetime, "event_type,", event_type, "equipment", equipment
    found = database[collection_names['events']].find_one({'hosts': {'$in': hosts},
                                                           'date': event_datetime,
                                                           'event_type': event_type,
                                                           'equipment': equipment})
    if create and found is None:
        database[collection_names['events']].insert({'hosts': hosts,
                                                     'date': event_datetime,
                                                     'equipment': equipment,
                                                     'event_type': event_type})
        return get_event(event_type, event_datetime, hosts, equipment, False)
    return found

def create_timeline_id(name):
    return (database[collection_names['timelines']].insert({'name': name}))

def get_timeline(id):
    return database[collection_names['timelines']].find_one({'_id': id})

def save_timeline(tl):
    d = tl.__dict__
    database[collection_names['timelines']].update({'_id': tl._id},
                                                   {'name': tl.name,
                                                    'events': [[te[0], event.as_id(te[1])]
                                                               # todo: sort out how to save these timestamp:event pairs
                                                               for te in tl.events]})

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
        person = get_person_dict(person)
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

def person_name0(person, viewing_person):
    """Return the person's full name and nickname.
    If they have requested anonymity, only they and the admins can see their name."""
    # todo: integrate with other name function
    person = get_person_dict(person)
    viewing_person = get_person_dict(viewing_person)
    if (person == viewing_person
        or not person.get("anonymized", False) # optional flag
        # todo: add an equipment arg to give context so that owners and trainers of that equipment can see this
        or is_administrator(viewing_person)):
        given_name = person['given_name']
        return given_name + " " + person['surname'], person.get('known_as', given_name)
    else:
        return "Anonymous", "Anon"

def person_email0(person, viewing_person):
    # todo: use name database
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
