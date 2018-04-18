#!/usr/bin/env python

import sys
sys.path.append('common')

from event import Event
from person import Person
import argparse
import configuration
import csv
import database
import yaml

def add_training(person, trainer, trained_date, equipment):
    if trainer:
        trainer = trainer._id
    event = Event.find('training', trained_date, [trainer], [equipment])
    person.add_event(event)

def main():
    # todo: convert all dates to datetime.datetime as mentioned in http://api.mongodb.com/python/current/examples/datetimes.html
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--members", default="members.csv")
    parser.add_argument("-u", "--users", default="users.csv")
    parser.add_argument("-o", "--owners", default="owners.csv")
    parser.add_argument("-t", "--trainers", default="trainers.csv")
    parser.add_argument("--delete-existing", action='store_true')
    args = parser.parse_args()
    config = configuration.get_config()
    db_config = config['database']
    collection_names = db_config['collections']
    print "collection names are", collection_names
    database.database_init(config, args.delete_existing)

    # todo: fix these
    # database[collection_names['people']].create_index('link_id')
    # database[collection_names['names']].create_index('link_id')

    with open(args.members) as members_file:
        for row in csv.DictReader(members_file):
            name_parts = row['Name'].rsplit(" ", 1)
            member_no = row['Member no']
            database.add_person({'membership_number': member_no,
                                 'email': row['Email'],
                                 'given_name': name_parts[0],
                                 'surname': name_parts[1],
                                 'known_as': name_parts[0]},
                                {'membership_number': member_no})
            added = Person.find(row['Name'])
            print "added person record", added
            add_training(added,
                         Person.find(row['Inductor']),
                         row['Date inducted'],
                         'Makespace')
            inducted = Person.find(row['Name'])
            print "inducted is", inducted, "with events", inducted.events
    with open(args.users) as users_file:
        for row in csv.DictReader(users_file):
            person = Person.find(row['Name'])
            add_training(person,
                         Person.find(row['Trainer']),
                         row['Date'],
                         row['Equipment'])
            checkback = Person.find(row['Name'])
            print "checkback is", checkback, "with events", checkback.events

if __name__ == "__main__":
    main()
