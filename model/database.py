#!/usr/bin/python

# Support functions for the modules intended to support the UI.
# The UI probably shouldn't call anything in this file directly.

from __future__ import print_function

import bson
import json
import model.configuration
import model.event
import model.person
import os
import pymongo
import re
import uuid

client = None
database = None
collection_names = None
database_initted = False

def database_init(config):
    global client, database, collection_names, database_initted
    if database_initted:
        return
    database_initted = True
    db_config = config['database']
    collection_names = db_config['collections']
    client = pymongo.MongoClient(db_config['URI'])
    database = client[db_config['database_name']]
    if database is None:
        raise ConnectionError

def get_person_dict(identification):
    """Read the data for a person from the database, as a dictionary."""
    if identification is None:
        return None
    if isinstance(identification, dict):
        return identification             # no lookup needed
    if isinstance(identification, model.person.Person):
        return identification.__dict__
    collection = database[collection_names['people']]
    return ((isinstance(identification, bson.objectid.ObjectId)
             and collection.find_one({'_id': identification}))
            or (isinstance(identification, str)
                and re.match("^[0-9a-fA-F]+$", identification)
                and collection.find_one({'_id': bson.objectid.ObjectId(identification)}))
            or collection.find_one({'link_id': identification})
            or collection.find_one({'fob': identification})
            # names and email addresses are kept in a separate database
            or collection.find_one({'link_id': name_to_id(identification)}))

# You should generally use these functions to get these details of
# people, rather than looking directly in the relevant fields of the
# record, so that privacy protection can be applied.

def get_person_profile_field(whoever,
                             profile_field,
                             role_viewed=None,
                             equipment=None,
                             default_value=None):
    """Return a profile field of a person.
    You should use model.person.get_profile_field() instead of this in your programs,
    as that handles the privacy controls."""
    person_link = (whoever['link_id']
                   if isinstance(whoever, dict)
                   else (whoever.link_id
                         if isinstance(whoever, model.person.Person)
                         else whoever))
    profile_record = database[collection_names['profiles']].find_one({'link_id': person_link})
    if profile_record is None:
        return default_value
    else:
        return profile_record.get(profile_field, default_value)

def set_person_profile_field(whoever,
                             profile_field,
                             new_value,
                             role_viewed=None,
                             equipment=None):
    """Return a profile field of a person.
    You should use model.person.set_profile_field() instead of this in your programs,
    as that handles the privacy controls."""
    person_link = (whoever['link_id']
                   if isinstance(whoever, dict)
                   else (whoever.link_id
                         if isinstance(whoever, model.person.Person)
                         else whoever))
    profile_record = database[collection_names['profiles']].find_one({'link_id': person_link})
    if profile_record is not None:
        profile_record[profile_field] = new_value
        database[collection_names['profiles']].save(profile_record)

def person_name(whoever,
                role_viewed=None,
                equipment=None):
    """Return the formal and informal names of a person.
    You should use model.person.name() instead of this in your programs,
    as that handles the privacy controls."""
    person_link = (whoever['link_id']
                   if isinstance(whoever, dict)
                   else (whoever.link_id
                         if isinstance(whoever, model.person.Person)
                         else whoever))
    name_record = database[collection_names['profiles']].find_one({'link_id': person_link})
    if name_record is None:
        return "unknown", "unknown"
    else:
        return (name_record.get('given_name', "?") + " " + name_record.get('surname', "?"),
                name_record.get('known_as', name_record.get('given_name', "?")))

def person_set_name(whoever, viewing_person, new_name):
    """Set the person's email address."""
    person_link = (whoever['link_id']
                   if isinstance(whoever, dict)
                   else (whoever.link_id
                         if isinstance(whoever, model.person.Person)
                         else whoever))
    name_record = database[collection_names['profiles']].find_one({'link_id': person_link})
    if name_record is None:
        print("Could not find", person_link, "to set their name")
    else:
        given_name, surname = new_name.split(' ', 1) # todo: -1?
        name_record['given_name'] = given_name
        name_record['surname'] = surname
    database[collection_names['profiles']].save(name_record)
    # todo: tell django that the name has changed

def person_email(whoever, viewing_person):
    """Return the person's email address.
    If they have requested anonymity, only they and the admins can see this."""
    person_link = (whoever['link_id']
                   if isinstance(whoever, dict)
                   else (whoever.link_id
                         if isinstance(whoever, model.person.Person)
                         else whoever))
    name_record = database[collection_names['profiles']].find_one({'link_id': person_link})
    if name_record is None:
        return "unknown@example.com"
    else:
        return name_record.get('email', "exists_but_no_email@example.com")

def person_set_email(whoever, viewing_person, new_email):
    """Set the person's email address."""
    person_link = (whoever['link_id']
                   if isinstance(whoever, dict)
                   else (whoever.link_id
                         if isinstance(whoever, model.person.Person)
                         else whoever))
    name_record = database[collection_names['profiles']].find_one({'link_id': person_link})
    if name_record is None:
        print("Could not find", person_link, "to set their email address")
    else:
        name_record['email'] = new_email
    database[collection_names['profiles']].save(name_record)
    # todo: tell django that the email address has changed

def name_to_id(name):
    name_parts = name.rsplit(" ", 1)
    collection = database[collection_names['profiles']]
    record = (collection.find_one({"surname" : name_parts[-1], "given_name" : name_parts[0]})
              if len(name_parts) >= 2
              else (collection.find_one({"known_as" : name})
                    or collection.find_one({"email" : name})))
    return record and record.get('link_id', None)

def add_person(name_record, main_record):
    # todo: convert dates to datetime.datetime
    link_id = str(uuid.uuid4())
    main_record['link_id'] = link_id # todo: make it index by this
    name_record['link_id'] = link_id # todo: make it index by this
    database[collection_names['people']].insert(main_record)
    database[collection_names['profiles']].insert(name_record)
    return link_id

def get_all_person_dicts():
    return [ whoever for whoever in database[collection_names['people']].find({}) ]

def save_person(somebody):
    database[collection_names['people']].save(somebody)

# Events

def get_event(event_type, event_datetime, hosts, equipment, create=True):
    """Read the data for an event from the database."""
    # print("Database looking for event", "hosts:", hosts, "date", event_datetime, "event_type:", event_type, "equipment", equipment)
    found = database[collection_names['events']].find_one({'hosts': {'$in': hosts},
                                                           'date': event_datetime,
                                                           'event_type': event_type,
                                                           'equipment': equipment})
    if found is None and create:
        # print("making new event in database")
        # print("get_event recursing")
        x = database[collection_names['events']].insert({'hosts': hosts,
                                                         'date': event_datetime,
                                                         'equipment': equipment,
                                                         'event_type': event_type})
        # print("result of db insert is", x)
        new_event = get_event(event_type, event_datetime, hosts, equipment, False)
        # print("returned from recursion, database new event is", new_event['_id'], "with", len(new_event.get('invitation_accepted', [])), "invitation_accepted")
        return new_event
    # print("database found event already", found['_id'])
    return found

def get_events(event_type=None,
               person_field=None, person_id=None,
               earliest=None, latest=None,
               include_hidden=False):
    """Get events matching various requirements."""
    query = {}
    if event_type:
        query['event_type'] = event_type
    if person_field and person_id:
        query[person_field] = {'$in': [person_id]}
    if not include_hidden:
        query['status'] = 'published'
    if earliest:
        query['start'] = {'$gt': earliest}
    if latest:
        query['end'] = {'$lt': latest}
    # print("get_events query", query)
    result = [ model.event.Event.find_by_id(tr_event['_id'])
               for tr_event in database[collection_names['events']].find(query).sort('start',
                                                                                     pymongo.ASCENDING) ]
    # print("get_events result", result, "with ids", [r._id for r in result])
    return result

def get_event_by_id(event_id):
    """Read the data for an event from the database."""
    return database[collection_names['events']].find_one({'_id': event_id})

def save_event(this_event):
    # print("saving event", this_event)
    if this_event['_id'] is None:
        del this_event['_id']
        database[collection_names['events']].insert(this_event)
    else:
        database[collection_names['events']].save(this_event)
    # print("saved event as", this_event)

# Notifications (to individuals)

def get_notifications(who_id, since_date):
    return [message
            for message in database[collection_names['notifications']].find({'to': who_id, 'when': {'$gt': since_date}})]

def add_notification(who_id, sent_date, text):
    database[collection_names['notifications']].insert({'to': who_id,
                                                        'when': sent_date,
                                                        'text': text})

# Announcements (to all)

def get_announcements(since_date):
    print("get_announcements query will be", {'when': {'$gt': since_date}}, "and the collection will be", database[collection_names['announcements']])
    return [message
            for message in database[collection_names['announcements']].find({'when': {'$gt': since_date}})]

def add_announcement(sent_date, from_id, text):
    database[collection_names['announcements']].insert({'when': sent_date,
                                                        'from': from_id,
                                                        'text': text})
# invitation replies

def find_rsvp(rsvp_uuid):
    print("find_rsvp collection name", collection_names['people'], "collection", database[collection_names['people']], "rsvp_uuid", rsvp_uuid)
    rsvp_dict = database[collection_names['people']].find_one({'invitations.'+rsvp_uuid: {'$exists': True}})
    if rsvp_dict is None:
        return None
    return rsvp_dict['_id']

# event templates

def find_event_template(name):
    return database[collection_names['event_templates']].find_one({'name': name})

def list_event_templates():
    return [ template for template in database[collection_names['event_templates']].find({}) ]

def add_template(template):
    database[collection_names['event_templates']].update({'title': template['title']},
                                                         template,
                                                         upsert=True)

# Access permissions

def is_administrator(person, writer=False):
    """Return whether a person is an administrator who can access other people's data in the database.
    With the optional third argument non-False, check whether they have write access too."""
    return (model.configuration.get_config()['organization']['database']
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

def get_eqtype_events(equipment_type, event_type, earliest=None, latest=None):
    query = {'event_type': event_type,
             'equipment_type': equipment_type}
    if earliest:
        query['start'] = {'$gt': earliest}
    if latest:
        query['end'] = {'$lt': latest}
    return [ model.event.Event.find_by_id(tr_event['_id'])
             for tr_event in database[collection_names['events']].find(query).sort('start', pymongo.DESCENDING) ]

# Equipment

def get_machine_dict(name):
    """Read the data for a machine from the database."""
    # if isinstance(name, machine.Machine):
    #     name = name._id
    collection = database[collection_names['machines']]
    return (collection.find_one({'name': name})
            or collection.find_one({'_id': name}))

def get_machine_dicts_for_type(eqty):
    """Read the data for machines of a given type from the database."""
    result = [ machine for machine in database[collection_names['machines']].find({'equipment_type': eqty}) ]
    # print("Looking for machines of type", eqty, "and got", result)
    return result

def add_machine(name, equipment_type,
                location=None, acquired=None):
    data = {'name': name,
            'equipment_type': equipment_type}
    if location:
        data['location'] = location
    if acquired:
        data['acquired'] = acquired
    database[collection_names['machines']].insert(data)

def save_machine(something):
    database[collection_names['machines']].save(something)

def log_machine_use(machine, person, when):
    database[collection_names['machine_logs']].insert({'start': when, 'machine': machine, 'user': person})

def get_machine_log(machine):
    return [ entry for entry in database[collection_names['machine_logs']].find({'machine': machine}).sort('start', pymongo.DESCENDING) ]

def get_user_log(user):
    return [ entry for entry in database[collection_names['machine_logs']].find({'user': user}).sort('start', pymongo.DESCENDING) ]

# training requests

def get_people_awaiting_training(event_type, equipment_type):
    query = {'training_requests': {'$elemMatch':
                                   {'event_type': event_type,
                                    'equipment_type': equipment_type}}}
    print("get_people_awaiting_training using query", query)
    return [who['_id'] for who in
            database[collection_names['people']]
            .find(query)
            .sort('training_requests.request_date', pymongo.ASCENDING)]

def find_interested_people(interests):
    print("Looking for people with interests", interests)
    return [ someone['_id']
             for someone
             # I don't think that works, but db.MakespacePeople.find({'profile.interests.Lifehacking': 2}) gets some
             # $elemMatch may help
             in database[collection_names['people']].find({'profile.interests': {
                 # '$elemMatch':
                 '$in':
                 interests}}) ]

# misc

def role_training(role):
    return role + "_training"

def role_untraining(role):
    return role + "_untraining"
