#!/usr/bin/python

import sys
sys.path.append('../common')

from nevow import flat
from nevow import tags as T
import config
import database
import pages

def people_table(people_machine_relations):
    return T.table[[T.tr[T.th[person['name']], # todo: will probably go via _id
                         T.td[person['since']], # todo: check the key I use for this
                         T.td[person['trained_by']]] # todo: check the key I use for this
                      for person in people_machine_relations]]

def equipment_class(machine_class):
    # todo: get data from config, and search database for users, owners, and trainers
    users = get_machine_class_people(machine_class, 'trained')
    owners = get_machine_class_people(machine_class, 'owners')
    trainers = get_machine_class_people(machine_class, 'trainers')
    page_body = []
    if users and len(users) > 0:
        page_body = page_body + [T.h2["Users"] + people_table(users)]
    if owners and len(owners) > 0:
        page_body = page_body + [T.h2["Owners"] + people_table(owners)]
    if trainers and len(trainers) > 0:
        page_body = page_body + [T.h2["Trainers"] + people_table(trainers)]
    return pages.page_string("Equipment class " + machine_class,
                             page_body)

def main():                     # for testing
    print equipment_class("CNC router")

if __name__ == "__main__":
    main()
