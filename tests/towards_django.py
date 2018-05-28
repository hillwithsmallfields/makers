#!/usr/bin/python

import argparse
import json
import os
import random
import sys
from datetime import datetime, timedelta
sys.path.append('model')
sys.path.append('utils')
import configuration
import context
import database
import importer
import person
import event
import equipment_type
import machine
import timeline
import timeslots

def print_heading(text):
    print
    print text
    print '-'*len(text)

def show_person(directory, somebody):
    name = somebody.name()
    known_as = somebody.nickname()
    email = somebody.get_email()
    if directory:
        old_stdout = sys.stdout
        sys.stdout = open(os.path.join(directory, name.replace(' ', '_') + ".txt"), 'w')
    print_heading(name)
    print somebody
    print "Known as", known_as
    print "Id", somebody._id
    if somebody.fob:
        print "Fob:", somebody.fob
    print_heading("Available")

    # training = { ev.start: ev for ev in (somebody.get_training_events(event_type='user_training')
    #                                      + somebody.get_training_events(event_type='owner_training')
    #                                      + somebody.get_training_events(event_type='trainer_training')) }
    # print_heading("Training attended")
    # for tr_date in sorted(training.keys()):
    #     session = training[tr_date]
    #     ev_type = session.event_type.replace('_', ' ').capitalize()
    #     equip = ",".join([equipment_type.Equipment_type.find(e).name
    #                       for e in session.equipment_types]).replace('_', ' ').capitalize()
    #     hosts =  ",".join([person.Person.find(host_id).name()
    #                        for host_id in session.hosts
    #                        if host_id is not None])
    #     print "  ", session.date, ev_type, ' '*(20-len(ev_type)), equip, ' '*(30 - len(equip)), hosts

    server_config = configuration.get_config()['server']
    server_base = server_config['base_url']
    machine_base = server_base + server_config['machines']

    all_remaining_types = equipment_type.Equipment_type.list_equipment_types()

    their_responsible_types = { ty.name: ty for ty in (somebody.get_equipment_types('trainer')
                                                     + somebody.get_equipment_types('owner')) }

    responsibles = []

    if len(their_responsible_types) > 0:
        for tyrawname in sorted(their_responsible_types.keys()):
            tyname = tyrawname.replace('_', ' ').capitalize()
            ty = their_responsible_types[tyrawname]
            responsibles.append({'type': tyname,
                                 'is_owner': somebody.is_owner(ty) is not None,
                                 'is_trainer': somebody.is_trainer(ty) is not None,
                                 'training': {
                                     # todo: handle all types of training requests?
                                     'pending_requests': len(ty.get_training_requests(role='user')),
                                     'next_training_events': [ ],
                                     'has_more_training_events': False},
                                 'equipment': [ { 'name': mc.name,
                                                  'url': machine_base + mc.name,
                                                  'status': mc.status}
                                                for mc in [ machine.Machine.find_by_id(machine_id)
                                                            for machine_id in ty.get_machines() ]]})
            if ty in all_remaining_types:
                all_remaining_types.remove(ty)
        print_heading("Equipment responsibilities")
        print responsibles

    used = []

    their_user_types = somebody.get_equipment_types('user')
    for ty in their_responsible_types:
        if ty in their_user_types:
            their_user_types.remove(ty)
    if len(their_user_types) > 0:
        keyed_types = { ty.name: ty for ty in their_user_types }
        for tyrawname in sorted(keyed_types.keys()):
            tyname = tyrawname.replace('_', ' ').capitalize()
            ty = keyed_types[tyrawname]
            used.append({'name': tyname,
                         'requested_owner_training': somebody.has_requested_training([ty._id], 'owner'),
                         'requested_trainer_training': somebody.has_requested_training([ty._id], 'trainer')})
            if ty in all_remaining_types:
                all_remaining_types.remove(ty)
        print_heading("Equipment used")
        print used

    # my_training_requests = somebody.get_training_requests()
    # my_individual_training_requests = []
    # for req in my_training_requests: # each stored training request is for a list of equipment types
    #     my_individual_training_requests += req['equipment_types']
    # my_request_names = [ equipment_type.Equipment_type.find_by_id(req).name for req in my_individual_training_requests ]
    # if len(all_remaining_types) > 0:
    #     print_heading("Other equipment")
    #     keyed_types = { ty.name.replace('_', ' ').capitalize(): ty for ty in all_remaining_types }
    #     for tyname in sorted(keyed_types.keys()):
    #         print tyname, ' '*(30-len(tyname)), "[Cancel training request]" if keyed_types[tyname].name in my_request_names else "[Request training]"

    # print_heading("Training requests")
    # for req in my_training_requests:
    #     print req['request_date'], req['event_type'].replace('_', ' '), ", ".join([equipment_type.Equipment_type.find(reqeq).name for reqeq in req['equipment_types']])

    # # print_heading("Create events")
    # # for evtitle in sorted([ ev['title'].replace('$', 'some ').capitalize() for ev in event.Event.list_templates([somebody], their_equipment_types) ]):
    # #     print "[ Create", evtitle, "]"
    # # # todo: show events signed up for

    # if somebody.is_auditor() or somebody.is_administrator():
    #     print_heading("Administrative actions")
    #     print "[User list]"

    #     if somebody.is_administrator():
    #         print "[Create special event]"

    # for field, title in [('hosts', 'hosting'), ('attendees', 'attending')]:
    #     my_events = timeline.Timeline.create_timeline(person_field=field, person_id=somebody._id).events
    #     if len(my_events) > 0:
    #         print_heading("Events I'm " + title)
    #         for tl_event in my_events:
    #             hosts = tl_event.hosts
    #             if hosts is None:
    #                 hosts = []
    #             print tl_event.start, tl_event.event_type + " "*(24-len(tl_event.event_type)), ", ".join([person.Person.find(ev_host).name()
    #                                                                   for ev_host in hosts
    #                                                                   if ev_host is not None])

    # interests = somebody.get_interests()
    # if len(interests) > 0:
    #     print_heading("Skills and interests")
    #     for (interest, level) in interests.iteritems():
    #         print interest.encode('utf-8') + ' '*(72 - len(interest)), ["none", "would like to learn", "already learnt", "can teach"][level]

    print_heading("Personal data for API (short)")
    print json.dumps(somebody.api_personal_data(), indent=4)
    print_heading("Personal data for API (full)")
    print json.dumps(somebody.api_personal_data(True), indent=4)
    if directory:
        sys.stdout.close()
        sys.stdout = old_stdout

def set_context_as_admin(context):
    context.add_role('owner', configuration.get_config()['organization']['database'])

def main():
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
    parser.add_argument("-q", "--quick", action='store_true')
    args = parser.parse_args()

    print "importing from spreadsheet files"
    importer.import0(args)

    context.Context.change_context(set_context_as_admin)

    print "Listing members"
    for whoever in person.Person.list_all_members():
        show_person("hack-pages", whoever)

    print "writing machine controller local cache data"
    with open("allfobs.json", 'w') as outfile:
        outfile.write(json.dumps(equipment_type.Equipment_type.API_all_equipment_fobs(), indent=4))

if __name__ == "__main__":
    main()
