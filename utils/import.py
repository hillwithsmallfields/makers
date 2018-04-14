#!/usr/bin/env python

import sys
sys.path.append('common')

import argparse
import csv
import configuration
import yaml
import database
from person import Person

def add_training(person, trainer, trained_date, equipment):
    if trainer:
        trainer = trainer._id
    event = database.get_event([trainer], trained_date, 'training', [equipment])
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
    database.database_init(config, args.delete_existing)
    with open(args.members) as members_file:
        for row in csv.DictReader(members_file):
            name_parts = row['Name'].rsplit(" ", 1)
            database.add_person({'given_name': name_parts[0],
                                 'surname': name_parts[1],
                                 'known_as': name_parts[0],
                                 'email': row['Email'],
                                 'membership_number': row['Member no']})
            added = Person.find(row['Email'])
            add_training(added,
                         Person.find(row['Inductor']),
                         row['Date inducted'],
                         'Makespace')
    with open(args.users) as users_file:
        for row in csv.DictReader(users_file):
            person = Person.find(row['Name'])
            add_training(person,
                         Person.find(row['Trainer']),
                         row['Date'],
                         row['Equipment'])
            checkback = Person.find(person.email)
            print "checkback is", checkback, "with events", checkback.events

if __name__ == "__main__":
    main()
