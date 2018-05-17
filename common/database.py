#!/usr/bin/python

# Support functions for the modules intended to support the UI.
# The UI probably shouldn't call anything in this file directly.

import configuration
from context import Context
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
        database.drop_collection(collection_names['equipment_types'])
        database.drop_collection(collection_names['equipment'])
        database.drop_collection(collection_names['events'])
        database.drop_collection(collection_names['event_templatess'])

def get_person_dict(identification):
    """Read the data for a person from the database, as a dictionary."""
    if identification is None:
        return None
    if isinstance(identification, dict):
        return identification             # no lookup needed
    if isinstance(identification, person.Person):
        return identification.__dict__
    collection = database[collection_names['people']]
    # print "get_person_dict lookup", identification
    return (collection.find_one({'_id': identification})
            or collection.find_one({'link_id': identification})
            or collection.find_one({'fob': identification})
            # names and email addresses are kept in a separate database
            or collection.find_one({'link_id': name_to_id(identification)}))

# You should generally use these functions to get these details of
# people, rather than looking directly in the relevant fields of the
# record, so that privacy protection can be applied.

def person_name(whoever,
                equipment=None, role_viewed=None):
    """Return the formal and informal names of a person, or not, if they're anonymous.
    Always use this to get someone's name; this way, anonymity is handled for you.
    For events, if you're being viewed in the host role, you can't be anonymous (for now)."""
    # todo: add admin override of anonymity
    person_link = (whoever['link_id']
                   if isinstance(whoever, dict)
                   else (whoever.link_id
                         if isinstance(whoever, person.Person)
                         else whoever))
    name_record = database[collection_names['names']].find_one({'link_id': person_link})
    if name_record is None:
        return "unknown", "unknown"
    if (not Context.get_context().can_read_for(equipment)
        and role_viewed != 'host'
        and name_record.get('anonymous', False)):
        if 'membership_number' in name_record:
            num_string = str(name_record['membership_number'])
            return "member " + num_string, num_string
        else:
            return "Anonymous member", "Anon"
    else:
        return (name_record.get('given_name', "?") + " " + name_record.get('surname', "?"),
                name_record.get('known_as', name_record.get('given_name', "?")))

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

def get_all_person_dicts():
    return [ whoever for whoever in database[collection_names['people']].find({}) ]

def save_person(somebody):
    database[collection_names['people']].save(somebody)

def get_people_awaiting_training(event_type, equipment_types):
    query = {'training_requests': {'$elem_match': {'event_type': event_type,
                                                   'equipment_types': {'$in': equipment_types}}}}
    return [ who for who in database[collection_names['people']].find(query) ]

# Events

def get_event(event_type, event_datetime, hosts, equipment, create=True):
    """Read the data for an event from the database."""
    # print "Looking for event", "hosts,", hosts, "date", event_datetime, "event_type,", event_type, "equipment", equipment
    found = database[collection_names['events']].find_one({'hosts': {'$in': hosts},
                                                           'date': event_datetime,
                                                           'event_type': event_type,
                                                           'equipment': equipment})
    if found is None and create:
        print "making new event in database"
        database[collection_names['events']].insert({'hosts': hosts,
                                                     'date': event_datetime,
                                                     'equipment': equipment,
                                                     'event_type': event_type})
        new_event = get_event(event_type, event_datetime, hosts, equipment, False)
        print "new event is", new_event
        return new_event
    return found

def get_events(event_type=None,
               person_field=None, person_id=None,
               as_far_back_as=None, as_recently_as=None,
               include_hidden=False):
    """Get events matching various requirements."""
    query = {}
    if event_type:
        query['event_type'] = event_type
    if person_field and person_id:
        query[person_field] = {'$in': [person_id]}
    if not include_hidden:
        query['status'] = 'published'
    if as_far_back_as:
        query['start'] = {'$gt': as_far_back_as}
    if as_recently_as:
        query['end'] = {'$lt': as_far_back_as}
    # print "get_events query", query
    result = [ event.Event.find_by_id(tr_event['_id'])
             for tr_event in database[collection_names['events']].find(query).sort('start',
                                                                                   pymongo.DESCENDING) ]
    # print "get_events result", result
    return result

def get_event_by_id(event_id):
    """Read the data for an event from the database."""
    return database[collection_names['events']].find_one({'_id': event_id})

def save_event(this_event):
    print "saving event", this_event
    database[collection_names['events']].save(this_event)

# event templates

def find_event_template(name):
    return database[collection_names['event_templates']].find_one({'event_type': name})

def list_event_templates():
    return [ template for template in database[collection_names['event_templates']].find({}) ]

def add_template(template):
    database[collection_names['event_templates']].insert(template)

# Access permissions

def is_administrator(person, writer=False):
    """Return whether a person is an administrator who can access other people's data in the database.
    With the optional third argument non-False, check whether they have write access too."""
    return (configuration.get_config()['organization']['database']
            in get_person_machines(person,
                                   'owner' if writer else 'trained'))

# Equipment types

def get_equipment_type_dict(clue):
    collection = database[collection_names['equipment_types']]
    return (collection.find_one({'_id': clue})
            or collection.find_one({'name': clue}))

def add_equipment_type(name, training_category,
                        manufacturer=None):
    data = {'name': name,
            'training_category': training_category}
    if manufacturer:
        data['manufacturer'] = manufacturer
    database[collection_names['equipment_types']].insert(data)

def list_equipment_types(training_category=None):
    query = {}
    if training_category:
        query['training_category'] = training_category
    return [ et for et in database[collection_names['equipment_types']].find(query) ]

def get_eqtype_events(equipment_type, event_type):
    return [ event.Event.find_by_id(tr_event['_id'])
             for tr_event in database[collection_names['events']].find({'event_type': event_type,
                                                                        'equipment_types': {'$in': [equipment_type]}}).sort('start', pymongo.DESCENDING) ]

# Equipment

def get_machine(name):
    """Read the data for a machine from the database."""
    collection = database[collection_names['equipment']]
    return (collection.find_one({'name': name})
            or collection.find_one({'_id': name}))

def add_machine(name, equipment_type,
                location=None, acquired=None):
    data = {'name': name,
            'equipment_type': equipment_type}
    if location:
        data['location'] = location
    if acquired:
        data['acquired'] = acquired
    database[collection_names['equipment']].insert(data)

# training requests

def get_training_queue(role, equipment_types):
    # todo: wrap this in a higher level that converts these to 'person' objects
    return [ somebody for somebody in database[collection_names['people']].find(
        { 'requests': { '$elemMatch': { 'event_type': role_training(role),
                                        # todo: check the sort spec (it seems to work but I'm not sure it looks right)
                                        'equipment_types': { '$in': equipment_types } } } }).sort('requests.request_date', pymongo.ASCENDING) ]

# misc

def role_training(role):
    return role + "_training"

def role_untraining(role):
    return role + "_untraining"
