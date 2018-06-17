#!/usr/bin/python

import argparse
import json
import os
import random
import sys
from datetime import datetime, timedelta

sys.path.append('model')
sys.path.append('utils')
sys.path.append('pages')

import access_permissions
import configuration
import database
import equipment_type
import event
import importer
import machine
import pages
import person
import timeline
import timeslots

import equipment_type_list_page
import equipment_type_page
import person_page

genconf = configuration.get_config()
interest_areas = genconf['skill_areas']

evening_timeslots = timeslots.timeslots_to_int([[False,False,True]]*7)
weekend_timeslots = timeslots.timeslots_to_int([[False,False,False]]* 5 + [[True,True,True]]*2)
evening_and_weekend_timeslots = evening_timeslots | weekend_timeslots

print "evening_timeslots:", timeslots.timeslots_from_int(evening_timeslots)
print "weekend_timeslots:", timeslots.timeslots_from_int(weekend_timeslots)
print "evening_and_weekend_timeslots:", timeslots.timeslots_from_int(evening_and_weekend_timeslots)

def set_access_permissions_as_admin(access_permissions):
    access_permissions.add_role('owner', configuration.get_config()['organization']['database'])

def setup_random_event(possible_templates, event_datetime, eqtypes, attendees, verbose=False):
    new_event, problem = event.Event.instantiate_template(random.choice(possible_templates)['event_type'],
                                                          eqtypes,
                                                          attendees,
                                                          event_datetime,
                                                          allow_past=True)
    if not problem:
        new_event.catered = (random.random() < 0.5)
        new_event.interest_areas = []
        for i in range(0, random.randrange(0,3)):
            new_event.interest_areas.append(random.choice(interest_areas))
        if verbose:
            print "Created event", new_event
        new_event.publish()
    else:
        if verbose:
            print "Failed to create event"

def random_user_activities(equipments, green_templates):
    for whoever in person.Person.list_all_people():
        membership = whoever.is_member()
        if membership[0]:
            whoever.available = evening_timeslots if random.random() < 0.2 else evening_and_weekend_timeslots
            date_joined = membership[0].start
            for i in range(1, random.randrange(1, 12)):
                days_since_joining = (datetime.now() - date_joined).days
                request_date = date_joined + timedelta(random.randrange(7, days_since_joining + 56), 0)
                equip = random.choice(equipments)
                role = 'user'
                if whoever.qualification(equip, role):
                    role = 'trainer'
                if whoever.qualification(equip, role):
                    role = 'owner'
                if whoever.qualification(equip, role):
                    continue
                whoever.add_training_request(role, [equip], request_date)
            my_trainer_types = whoever.get_equipment_types('trainer')
            if len(my_trainer_types) > 0:
                possible_templates = green_templates + event.Event.list_templates([whoever], my_trainer_types)
                for i in range(1, random.randrange(1, 3)):
                    event_datetime = datetime.now() + timedelta(random.randrange(-30,30))
                    setup_random_event(possible_templates, event_datetime, [random.choice(my_trainer_types)._id], [whoever._id])
            if random.random() < 0.1:
                whoever.profile['avoidances'] = ['vegetarian']
                if random.random() < 0.05:
                    whoever.profile['avoidances'].append('gluten-free')
                if random.random() < 0.05:
                    whoever.profile['avoidances'].append('ketogenic')
                whoever.save()
            for x in range(0, random.randrange(0, 3)):
                whoever.add_interest(random.choice(interest_areas),
                                     random.randrange(1, 3))
            # todo: sign up for training at random
        else:
            "no membership found for", whoever

def make_training_event_template(eqty):
    return { 'event_type': 'user training',
             'title': eqty.name + ' user training',
             'attendance_limit': 6,
             'host_prerequisites':   [ eqty.name + ' trainer' ],
             'attendee_prerequisites': [ 'member' ] }

def names(ids, role):
    return ", ".join([obj.name(access_permissions_role=role)
                      for obj in [person.Person.find(id) for id in ids]
                      if obj is not None])

def show_person(directory, somebody):
    name = somebody.name()
    with open(os.path.join(directory, name.replace(' ', '_') + ".html"), 'w') as pagefile:
        pagefile.write(pages.page_string("Dashboard for "+name,
                                         person_page.person_page_contents(somebody, somebody)))

def show_equipment_types():
    with open(os.path.join("equipment-type-pages", "equipment-type-index.html"), 'w') as pagefile:
        pagefile.write(pages.page_string("Equipment types by category",
                                         [equipment_type_list_page.equipment_type_list_section(training_category)
                                          for training_category in ['green', 'amber', 'red']]))
    for eqty in equipment_type.Equipment_type.list_equipment_types(None):
        with open(os.path.join("equipment-type-pages", eqty.name + ".html"), 'w') as pagefile:
            pagefile.write(pages.page_string(eqty.pretty_name(), equipment_type_page.equipment_type_section(eqty)))

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
    parser.add_argument("-x", "--existing", "--no-import", action='store_true')
    args = parser.parse_args()

    config = configuration.get_config()

    access_permissions.Access_Permissions.change_access_permissions(set_access_permissions_as_admin)

    days, slots, order = timeslots.get_slots_conf()
    print "periods are", slots, "in order", order

    if not args.existing:
        print "importing from spreadsheet files"
        importer.import0(args)
    else:
        database.database_init(config, args.delete_existing)

    print "import complete, running random user behaviour"
    all_types = equipment_type.Equipment_type.list_equipment_types()
    green_equipment = equipment_type.Equipment_type.list_equipment_types('green')
    green_templates = [ make_training_event_template(eqty) for eqty in green_equipment ]
    print "green templates are", green_templates

    if not args.existing:
        random_user_activities(all_types, green_templates)

    if not args.quick:
        print "listing members"
        all_members = person.Person.list_all_members()
        for whoever in all_members:
            show_person("member-pages", whoever)

    show_equipment_types()

if __name__ == "__main__":
    main()
