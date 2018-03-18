#!/usr/bin/python

import sys
sys.path.append('common')

import argparse
import csv
import configuration
import yaml
import database

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
                                 'date_joined': row['Date inducted'],
                                 'inducted_by': row['Inductor'],
                                 'email': row['Email']})
    with open(args.users) as users_file:
        for row in csv.DictReader(users_file):
            name = row['Name']
            person = database.get_person(name)
            trainer_name = row['Trainer']
            trainer = database.get_person(trainer_name)
            if trainer:
                trainer = trainer['_id']
            print "Will mark", person, "as users of", row['Equipment'], "trained by", trainer, "on", row['Date']
            # todo: use update_one


if __name__ == "__main__":
    main()
