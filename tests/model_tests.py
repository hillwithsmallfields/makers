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
import database
import importer
import person
import event
import equipment_type
import timeline
import timeslots

genconf = configuration.get_config()
interest_areas = genconf['skill_areas']

evening_timeslots = timeslots.timeslots_to_int([[False,False,True]]*7)
weekend_timeslots = timeslots.timeslots_to_int([[False,False,False]]* 5 + [[True,True,True]]*2)
evening_and_weekend_timeslots = evening_timeslots | weekend_timeslots

print "evening_timeslots:", timeslots.timeslots_from_int(evening_timeslots)
print "weekend_timeslots:", timeslots.timeslots_from_int(weekend_timeslots)
print "evening_and_weekend_timeslots:", timeslots.timeslots_from_int(evening_and_weekend_timeslots)

def random_user_activities(equipments, green_templates):
    for whoever in person.Person.list_all_people():
        membership = whoever.is_member()
        if membership:
            whoever.available = evening_timeslots if random.random() < 0.2 else evening_and_weekend_timeslots
            date_joined = membership.start
            for i in range(1, random.randrange(1, 4)):
                request_date = date_joined + timedelta(random.randrange(7, 56), 0)
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
                    template = random.choice(possible_templates)
                    event_datetime = datetime.now() + timedelta(random.randrange(-30,30))
                    new_event, problem = event.Event.instantiate_template(template['event_type'],
                                                                          [random.choice(my_trainer_types)._id],
                                                                          [whoever._id],
                                                                          event_datetime,
                                                                          allow_past=True)
                    if not problem:
                        new_event.catered = (random.random() < 0.5)
                        new_event.interest_areas = []
                        for i in range(0, random.randrange(0,3)):
                            new_event.interest_areas.append(random.choice(interest_areas))
                        new_event.publish()
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

def print_heading(text):
    print
    print text
    print '-'*len(text)

def list_equipment_types_to_files(all_types):
    print "Listing equipment types"
    for eqtype in all_types:
        old_stdout = sys.stdout
        sys.stdout = open(os.path.join("equipment-type-pages", eqtype.name.replace(' ', '_') + ".txt"), 'w')
        print "  users", ", ".join([ user.name() for user in eqtype.get_trained_users() ])
        print "  owners",  ", ".join([ user.name() for user in eqtype.get_owners() ])
        print "  trainers",  ", ".join([ user.name() for user in eqtype.get_trainers() ])
        print "  machines",  ", ".join([ machine.Machine.find_by_id(mc).name for mc in eqtype.get_machines() ])
        print "  enabled fobs", json.dumps(eqtype.API_enabled_fobs(), indent=4)
        for role in ['user', 'owner', 'trainer']:
            requests = database.get_people_awaiting_training(role, [eqtype._id])
            print_heading(role + " requests")
            for req in requests:
                print "  ", req
                # print req.name()
        sys.stdout.close()
        sys.stdout = old_stdout

def names(ids, role):
    return ", ".join([obj.name(context_role=role)
                      for obj in [person.Person.find(id) for id in ids]
                      if obj is not None])

def list_all_events():
    print_heading("All events")
    events = timeline.Timeline.create_timeline()
    for tl_event in events.events:
        hosts = tl_event.hosts
        if hosts is None:
            hosts = []
        print tl_event.start, tl_event.event_type, ", ".join([person.Person.find(ev_host).name(context_role='host',
                                                                                               context_equipment=tl_event.equipment_types)
                                                              for ev_host in hosts
                                                              if ev_host is not None])
        old_stdout = sys.stdout
        sys.stdout = open(os.path.join("event-pages", str(tl_event.start)), 'w')
        print "Event type", tl_event.event_type
        print "For equipment types", ", ".join ([ eqtyob.name
                                  for eqtyob in [ equipment_type.Equipment_type.find_by_id(eqty)
                                                  for eqty in tl_event.equipment_types ]
                       if eqtyob is not None ])
        print "Hosted by", names(tl_event.hosts, 'host')
        # todo: some stuff from around here is not appearing
        print "Attendees", names(tl_event.attendees, 'attendee')
        avoidances = tl_event.dietary_avoidances_summary()
        if tl_event.catered and avoidances and len(avoidances) > 0:
            print "Dietary Avoidances Summary:"
            for avpair in avoidances:
                print avpair[0] + ' '*(48 - len(avpair[0])), avpair[1]
        if tl_event.interest_areas:
            print "Interest areas:", ", ".join(tl_event.interest_areas)
            possibles = tl_event.possibly_interested_people()
            if len(possibles) > 0:
                print "Possibly interested:", names(possibles)
        sys.stdout.close()
        sys.stdout = old_stdout

def show_timeslots(avail):
    ts_config = configuration.get_config()['timeslots']
    days = ts_config['days']
    max_day_chars = reduce(max, map(len, days))
    times = ts_config['times']
    max_time_chars = reduce(max, map(len, times))
    print " " * max_day_chars, " ".join([ time + " " * (max_time_chars - len(time)) for time in times])
    for (day, day_slots) in zip(days, timeslots.timeslots_from_int(avail)):
        print day + " " * (max_day_chars - len(day)), " " * (max_time_chars/3), " ".join([ (("[*]" if slot else "[ ]") + (" " * (max_time_chars - 3))) for slot in day_slots[0:3] ])
        
def show_person(directory, somebody):
    name, known_as = database.person_name(somebody)
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
    show_timeslots(somebody.available)
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

    their_equipment_types = set(somebody.get_equipment_types('user'))
    keyed_types = { ty.name.replace('_', ' ').capitalize(): ty for ty in their_equipment_types }
    if len(their_equipment_types) > 0:
        print_heading("User")
        for tyname in sorted(keyed_types.keys()):
            ty = keyed_types[tyname]
            buttons = []
            if not (somebody.is_owner(ty._id) or somebody.has_requested_training([ty._id], 'owner')):
                buttons.append("[Request owner training]")
            if not (somebody.is_trainer(ty._id) or somebody.has_requested_training([ty._id], 'trainer')):
                buttons.append("[Request trainer training]")
            print tyname, ' '*(30-len(tyname)), " ".join(buttons)
            all_remaining_types -= their_equipment_types
    for role, button in [('trainer', '[Schedule training session]'),
                         ('owner', '[Schedule maintenance session]')]:
        their_equipment_types = set(somebody.get_equipment_types(role))
        if len(their_equipment_types) > 0:
            print_heading(role.capitalize())
            for tyname in sorted([ ty.name.replace('_', ' ').capitalize() for ty in their_equipment_types ]):
                print tyname, ' '*(30-len(tyname)), button
            all_remaining_types -= their_equipment_types

    my_training_requests = somebody.get_training_requests()
    my_individual_training_requests = []
    for req in my_training_requests: # each stored training request is for a list of equipment types
        my_individual_training_requests += req['equipment_types']
    my_request_names = [ equipment_type.Equipment_type.find_by_id(req).name for req in my_individual_training_requests ]
    if len(all_remaining_types) > 0:
        print_heading("Other equipment")
        keyed_types = { ty.name.replace('_', ' ').capitalize(): ty for ty in all_remaining_types }
        for tyname in sorted(keyed_types.keys()):
            print tyname, ' '*(30-len(tyname)), "[Cancel training request]" if keyed_types[tyname].name in my_request_names else "[Request training]"

    print_heading("Training requests")
    for req in my_training_requests:
        print req['request_date'], req['event_type'].replace('_', ' '), ", ".join([equipment_type.Equipment_type.find(reqeq).name for reqeq in req['equipment_types']])

    print_heading("Create events")
    for evtitle in sorted([ ev['title'].replace('$', 'some ').capitalize() for ev in event.Event.list_templates([somebody], their_equipment_types) ]):
        print "[ Create", evtitle, "]"
    # todo: show events signed up for

    if somebody.is_auditor() or somebody.is_administrator():
        print_heading("Administrative actions")
        print "[User list]"

        if somebody.is_administrator():
            print "[Create special event]"

    for field, title in [('hosts', 'hosting'), ('attendees', 'attending')]:
        my_events = timeline.Timeline.create_timeline(person_field=field, person_id=somebody._id).events
        if len(my_events) > 0:
            print_heading("Events I'm " + title)
            for tl_event in my_events:
                hosts = tl_event.hosts
                if hosts is None:
                    hosts = []
                print tl_event.start, tl_event.event_type + " "*(24-len(tl_event.event_type)), ", ".join([person.Person.find(ev_host).name()
                                                                      for ev_host in hosts
                                                                      if ev_host is not None])

    interests = somebody.get_interests()
    if len(interests) > 0:
        print_heading("Skills and interests")
        for (interest, level) in interests.iteritems():
            print interest.encode('utf-8') + ' '*(72 - len(interest)), ["none", "would like to learn", "already learnt", "can teach"][level]

    print_heading("Personal data for API (short)")
    print json.dumps(somebody.api_personal_data(), indent=4)
    print_heading("Personal data for API (full)")
    print json.dumps(somebody.api_personal_data(True), indent=4)
    if directory:
        sys.stdout.close()
        sys.stdout = old_stdout

def test_training_requests():
    guinea_pig = random.choice(person.Person.list_all_members())
    chosen_tool = random.choice(equipment_type.Equipment_type.list_equipment_types())
    roles = ['user', 'owner', 'trainer']
    print "Using", guinea_pig.name(), "as guinea pig, with tool", chosen_tool
    show_person("before", guinea_pig)
    for adding_role in roles:
        print "    About to add request", adding_role, chosen_tool
        for checking_role in roles:
            print "        Have they already got", checking_role, "?"
            print "        ", guinea_pig.has_requested_training([chosen_tool._id], checking_role)
        guinea_pig.add_training_request(adding_role, [chosen_tool])
        print "    Added request", adding_role, chosen_tool
        for checking_role in roles:
            print "        Have they now got", checking_role, "?"
            print "        ", guinea_pig.has_requested_training([chosen_tool._id], checking_role)
    show_person("after", guinea_pig)

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

    print "import complete, running random user behaviour"
    all_types = equipment_type.Equipment_type.list_equipment_types()
    green_templates = [ make_training_event_template(eqty) for eqty in equipment_type.Equipment_type.list_equipment_types('green') ]
    print "green templates are", green_templates
    random_user_activities(all_types, green_templates)

    test_training_requests()

    if not args.quick:
        print "listing members"
        for whoever in person.Person.list_all_members():
            show_person("member-pages", whoever)

    list_all_events()

    list_equipment_types_to_files(all_types)

    with open("allfobs.json", 'w') as outfile:
        outfile.write(json.dumps(equipment_type.Equipment_type.API_all_equipment_fobs(), indent=4))

if __name__ == "__main__":
    main()
