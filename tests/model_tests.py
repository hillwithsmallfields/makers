#!/usr/bin/python

import argparse
import json
import os
import random
import sys
from datetime import datetime, timedelta
sys.path.append('common')
sys.path.append('utils')
import database
import importer
import person
import event
import equipment_type

def random_user_activities(equipments):
    for whoever in person.Person.list_all_people():
        date_joined = whoever.is_member().start
        for i in range(1, random.randrange(1, 4)):
            request_date = date_joined + timedelta(random.randrange(7, 56), 0)
            equip = random.choice(equipments)
            # print whoever, "requests", equip, "on", request_date
            role = 'user'
            if whoever.qualification(equip, role):
                role = 'trainer'
            if whoever.qualification(equip, role):
                role = 'owner'
            if whoever.qualification(equip, role):
                continue
            whoever.add_training_request(role, [equip], request_date)

def print_heading(text):
    print
    print text
    print '-'*len(text)

def show_person(directory, somebody):
    old_stdout = sys.stdout
    name, known_as = database.person_name(somebody)
    sys.stdout = open(os.path.join(directory, name.replace(' ', '_') + ".txt"), 'w')
    print_heading(name)
    print somebody
    print "Known as", known_as
    print "Id", somebody._id
    if somebody.fob:
        print "Fob:", somebody.fob
    training = { ev.start: ev for ev in (somebody.get_training_events(event_type='user_training')
                                         + somebody.get_training_events(event_type='owner_training')
                                         + somebody.get_training_events(event_type='trainer_training')) }
    print_heading("Training attended")
    for tr_date in sorted(training.keys()):
        session = training[tr_date]
        ev_type = session.event_type.replace('_', ' ').capitalize()
        equip = ",".join([equipment_type.Equipment_type.find(e).name
                          for e in session.equipment_types]).replace('_', ' ').capitalize()
        hosts =  ",".join([person.Person.find(host_id).name()
                           for host_id in session.hosts
                           if host_id is not None])
        print "  ", session.date, ev_type, ' '*(20-len(ev_type)), equip, ' '*(30 - len(equip)), hosts
    all_remaining_types = set(equipment_type.Equipment_type.list_equipment_types())

    their_equipment_types = set(somebody.get_equipment_classes('user'))
    keyed_types = { ty.name.replace('_', ' ').capitalize(): ty for ty in their_equipment_types }
    if len(their_equipment_types) > 0:
        print_heading("User")
        for tyname in sorted(keyed_types.keys()):
            ty = keyed_types[tyname]
            buttons = []
            if not somebody.is_owner(ty._id):
                buttons.append("[Request owner training]")
            if not somebody.is_trainer(ty._id):
                buttons.append("[Request trainer training]")
            print tyname, ' '*(30-len(tyname)), " ".join(buttons)
            all_remaining_types -= their_equipment_types
    for role, button in [('trainer', '[Schedule training session]'),
                         ('owner', '[Schedule maintenance session]')]:
        their_equipment_types = set(somebody.get_equipment_classes(role))
        if len(their_equipment_types) > 0:
            print_heading(role.capitalize())
            for tyname in sorted([ ty.name.replace('_', ' ').capitalize() for ty in their_equipment_types ]):
                print tyname, ' '*(30-len(tyname)), button
            all_remaining_types -= their_equipment_types
    if len(all_remaining_types) > 0:
        print_heading("Other equipment")
        for tyname in sorted([ ty.name.replace('_', ' ').capitalize() for ty in all_remaining_types ]):
            # todo: filter out request button for equipment for which the user already has a request
            print tyname, ' '*(30-len(tyname)), "[Request training]"

    print_heading("Training requests")
    for req in somebody.get_training_requests():
        print req['request_date'], req['event_type'], [equipment_type.Equipment_type.find(reqeq).name for reqeq in req['equipment_types']]

    print_heading("Create events")
    for evtitle in sorted([ ev['title'].replace('$', 'some ').capitalize() for ev in event.Event.list_templates([somebody], their_equipment_types) ]):
        print evtitle

    # todo: fix these
    # if somebody.is_auditor() or somebody.is_admin():
    #     print "[User list]"

    # if somebody.is_admin():
    #     print "[Create special event]"

    print_heading("personal data for API")
    print json.dumps(somebody.api_personal_data(), indent=4)
    sys.stdout.close()
    sys.stdout = old_stdout

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--equipment-types", default="equipment-types.csv")
    parser.add_argument("-e", "--equipment", default="equipment.csv")
    parser.add_argument("-m", "--members", default="members.csv")
    parser.add_argument("-u", "--users", default="users.csv")
    parser.add_argument("-o", "--owners", default="owners.csv")
    parser.add_argument("-t", "--trainers", default="trainers.csv")
    parser.add_argument("-b", "--templates", default="event_templates")
    parser.add_argument("--delete-existing", action='store_true')
    parser.add_argument("-v", "--verbose", action='store_true')
    args = parser.parse_args()
    print "importing from spreadsheet files"
    importer.import0(args)
    print "import complete, running random user behaviour"
    all_types = equipment_type.Equipment_type.list_equipment_types()
    random_user_activities(all_types)
    # print "scanning list of people"
    # for whoever in person.Person.list_all_people():
    #     show_person("user-pages", whoever)
    print "listing members"
    for whoever in person.Person.list_all_members():
        show_person("member-pages", whoever)
    print "Listing equipment types"
    print "Equipment types are:", all_types
    for eqtype in all_types:
        old_stdout = sys.stdout
        sys.stdout = open(os.path.join("equipment-type-pages", eqtype.name.replace(' ', '_') + ".txt"), 'w')
        print "  users", [ user.name() for user in eqtype.get_trained_users() ]
        print "  owners",  [ user.name() for user in eqtype.get_owners() ]
        print "  trainers",  [ user.name() for user in eqtype.get_trainers() ]
        print "  enabled fobs", json.dumps(eqtype.API_enabled_fobs(), indent=4)
        for role in ['user', 'owner', 'trainer']:
            requests = database.get_training_queue(role, [eqtype._id])
            print_heading(role + " requests")
            for req in requests:
                print "  ", req
                # print req.name()
        sys.stdout.close()
        sys.stdout = old_stdout
    with open("allfobs.json", 'w') as outfile:
        outfile.write(json.dumps(equipment_type.Equipment_type.API_all_equipment_fobs(), indent=4))
