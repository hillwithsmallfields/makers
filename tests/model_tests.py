#!/usr/bin/python

import argparse
import json
import os
import random
import sys
from datetime import datetime, timedelta
sys.path.append('model')
sys.path.append('utils')
import access_permissions
import configuration
import database
import equipment_type
import event
import importer
import machine
import person
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
        if membership:
            whoever.available = evening_timeslots if random.random() < 0.2 else evening_and_weekend_timeslots
            date_joined = membership.start
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

def print_heading(text):
    print
    print text
    print '-'*len(text)

def list_equipment_types_to_files(all_types):
    for eqtype in all_types:
        old_stdout = sys.stdout
        sys.stdout = open(os.path.join("equipment-type-pages", eqtype.name.replace(' ', '_') + ".txt"), 'w')
        print "  users", ", ".join([ user.name() for user in eqtype.get_trained_users() ])
        print "  owners",  ", ".join([ user.name() for user in eqtype.get_owners() ])
        print "  trainers",  ", ".join([ user.name() for user in eqtype.get_trainers() ])
        print "  machines",  ", ".join([ machine.Machine.find_by_id(mc).name for mc in eqtype.get_machines() ])
        print "  enabled fobs", json.dumps(eqtype.API_enabled_fobs(), indent=4)
        for role in ['user', 'owner', 'trainer']:
            requests = eqtype.get_training_requests()
            print_heading(role + " requests")
            for req_person, req_req in requests.iteritems():
                print "  ", person.Person.find(req_person), req_req
                # print req.name()
        sys.stdout.close()
        sys.stdout = old_stdout

def names(ids, role):
    return ", ".join([obj.name(access_permissions_role=role)
                      for obj in [person.Person.find(id) for id in ids]
                      if obj is not None])

def show_event(tl_event):
    hosts = tl_event.hosts
    if hosts is None:
        hosts = []
    print tl_event.start, tl_event.event_type, ", ".join([person.Person.find(ev_host).name(access_permissions_role='host',
                                                                                           access_permissions_equipment=tl_event.equipment_types)
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

def list_all_events():
    old_stdout = sys.stdout
    sys.stdout = open(os.path.join("event-pages", "index.txt"), 'w')
    print_heading("All events")
    events = timeline.Timeline.create_timeline()
    for tl_event in events.events:
        show_event(tl_event)
    sys.stdout.close()
    sys.stdout = old_stdout

def test_event_time_filtering():
    events = timeline.Timeline.create_timeline()
    event_list = events.events
    event_count = len(event_list)
    early_split = event_list[event_count/3].start
    mid_split = event_list[event_count/2].start
    late_split = event_list[2*(event_count)/3].start
    print "total events", event_count
    print "early_split is", early_split
    print "mid_split is", mid_split
    print "late_split is", late_split
    first_half = timeline.Timeline.create_timeline(latest=mid_split)
    second_half = timeline.Timeline.create_timeline(earliest=mid_split)
    first_third = timeline.Timeline.create_timeline(latest=early_split)
    middle_third = timeline.Timeline.create_timeline(earliest=early_split, latest=late_split)
    last_third = timeline.Timeline.create_timeline(earliest=late_split)
    print "first_half", len(first_half.events)
    print "second_half", len(second_half.events)
    print "first_third", len(first_third.events)
    print "middle_third", len(middle_third.events)
    print "last_third", len(last_third.events)
    print "shortfall by halving:", event_count - (len(first_half.events) + len(second_half.events))
    print "shortfall by thirding:", event_count - (len(first_third.events) + len(middle_third.events) + len(last_third.events))

def show_timeslots(avail):
    days, _, times = timeslots.get_slots_conf()
    max_day_chars = reduce(max, map(len, days))
    max_time_chars = reduce(max, map(len, times))
    print " " * max_day_chars, " ".join([ time + " " * (max_time_chars - len(time)) for time in times])
    for (day, day_slots) in zip(days, timeslots.timeslots_from_int(avail)):
        print day + " " * (max_day_chars - len(day)), " " * (max_time_chars/3), " ".join([ (("[*]" if slot else "[ ]") + (" " * (max_time_chars - 3))) for slot in day_slots[0:3] ])

def show_all_machine_status():
    print_heading("Machine status")
    for eqty in equipment_type.Equipment_type.list_equipment_types():
        print "  ", eqty.name
        for machine_id in eqty.get_machines():
            mc = machine.Machine.find_by_id(machine_id)
            status, detail = mc.get_status()
            print "    ", mc.name, status, detail or ""

def show_events(title, events_timeline):
    if len(events_timeline.events) > 0:
        print_heading(title + configuration.get_config()['organization']['name'])
        for ev in events_timeline.events:
            print event.timestring(ev.start), ev.title, "with", ", ".join([person.Person.find(ev_host).name() for ev_host in ev.hosts])

def show_current_events():
    show_events("Now on in ", timeline.Timeline.present_events())

def show_coming_events():
    show_events("Next events at ", timeline.Timeline.future_events())

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
    show_timeslots(somebody.available)
    training = { ev.start: ev for ev in (somebody.get_training_events(event_type='user_training',
                                                                      when=datetime.now())
                                         + somebody.get_training_events(event_type='owner_training',
                                                                        when=datetime.now())
                                         + somebody.get_training_events(event_type='trainer_training',
                                                                        when=datetime.now())) }
    print_heading("Training attended")
    for tr_date in sorted(training.keys()):
        session = training[tr_date]
        ev_type = session.event_type.replace('_', ' ').capitalize()
        equip = ",".join([equipment_type.Equipment_type.find(e).name
                          for e in session.equipment_types]).replace('_', ' ').capitalize()
        hosts =  ",".join([person.Person.find(host_id).name()
                           for host_id in session.hosts
                           if host_id is not None])
        print "  ", event.timestring(session.date), ev_type, ' '*(20-len(ev_type)), equip, ' '*(30 - len(equip)), hosts
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
        print event.timestring(req['request_date']), req['event_type'].replace('_', ' '), ", ".join([equipment_type.Equipment_type.find(reqeq).name for reqeq in req['equipment_types']])

    print_heading("Create events")
    for evtitle in sorted([ ev['title'].replace('$', 'some ').capitalize() for ev in event.Event.list_templates([somebody], their_equipment_types) ]):
        print "[ Create", evtitle, "]"
    # todo: show events signed up for

    if somebody.is_auditor() or somebody.is_administrator():
        print_heading("Administrative actions")
        print "[User list]"

        if somebody.is_administrator():
            print "[Create special event]"

    known_events =[]

    for in_future in [True, False]:
        for field, title in [('hosts',
                              ('will be hosting' if in_future else 'have hosted')),
                             ('attendees',
                              ('will be attending' if in_future else 'have attended'))]:
            my_events = (timeline.Timeline.future_events(person_field=field, person_id=somebody._id).events
                         if in_future
                         else timeline.Timeline.past_events(person_field=field, person_id=somebody._id).events)
            if len(my_events) > 0:
                print_heading("Events I " + title)
                for tl_event in my_events:
                    known_events.append(tl_event)
                    hosts = tl_event.hosts
                    if hosts is None:
                        hosts = []
                    print event.timestring(tl_event.start), tl_event.event_type + " "*(24-len(tl_event.event_type)), ", ".join([person.Person.find(ev_host).name()
                                                                          for ev_host in hosts
                                                                          if ev_host is not None])

    pending_events = [ ev
                       for ev in timeline.Timeline.future_events().events
                       if ev not in known_events ]

    if len(pending_events) > 0:
        print_heading("Other future events")
        for pending_event in pending_events:
            hosts = pending_event.hosts
            if hosts is None:
                hosts = []
            if somebody._id in hosts:
                continue
            print event.timestring(pending_event.start), pending_event.event_type + " "*(24-len(pending_event.event_type)), ", ".join([person.Person.find(ev_host).name()
                                                                                                                                       for ev_host in hosts
                                                                                                                                       if ev_host is not None]), "[Sign up]"

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

def make_admin_people_index(members):
    sorting = { n[-1] + ", " + n[0]: m for n, m in [ (member.name().split(), member) for member in members ] }
    longest_name = reduce(max, map(len, [m.name() for m in members])) + 1
    old_stdout = sys.stdout
    sys.stdout = open(os.path.join("member-pages", "index.txt"), 'w')
    for name in sorted(sorting.keys()):
        who = sorting[name]
        their_name = who.name()
        roles_string = '; '.join([ role + ':' +', '.join(eq_with_role)
                                   for (role, eq_with_role) in [ (r, sorted(who.get_equipment_type_names(r)))
                                                                 for r in [ 'user', 'trainer', 'owner' ]]
                                   if len(eq_with_role) > 0 ])
        print their_name, ' '*(longest_name - len(their_name)), "%-5s" % who.membership_number, roles_string
    sys.stdout.close()
    sys.stdout = old_stdout

def write_mail_aliases(eq_types):
    old_stdout = sys.stdout
    sys.stdout = open("mail-aliases", 'w')
    for eqty in eq_types:
        for role in ['user', 'trainer', 'owner']:
            people_in_role = eqty.get_people(role)
            if len(people_in_role) > 0:
                print eqty.name+"-"+role+"s:", ",".join([whoever.get_email() for whoever in people_in_role])
    sys.stdout.close()
    sys.stdout = old_stdout

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

    test_time_to_timeslot = False
    if test_time_to_timeslot:
        for day in range(1, 8):
            for hour in range(0, 24):
                when = datetime(2000, 1, day, hour)
                slot_bitmap = timeslots.time_to_timeslot(when)
                print "day", days[when.weekday()], "hour", hour, "slot", "%x" % slot_bitmap

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

    test_training_requests()

    if not args.quick:
        print "listing members"
        all_members = person.Person.list_all_members()
        for whoever in all_members:
            show_person("member-pages", whoever)
        make_admin_people_index(all_members)

    print "listing events"
    list_all_events()

    print "testing event time filtering"
    test_event_time_filtering()

    print "listing equipment types"
    list_equipment_types_to_files(all_types)

    print "writing machine controller local cache data"
    with open("allfobs.json", 'w') as outfile:
        outfile.write(json.dumps(equipment_type.Equipment_type.API_all_equipment_fobs(), indent=4))

    # make sure there are some events going on right now, for show_current_events to show:
    # todo: find why it's failing to create these events, then fix it, then see whether the "current event" code is working
    everybody = person.Person.list_all_people()
    for _ in range(1, random.randrange(3, 7)):
        event_datetime = datetime.now()
        event_datetime = event_datetime.replace(hour=event_datetime.hour-random.randrange(0,2), minute=0, second=0, microsecond=0)
        print "Making current event starting at", event_datetime
        setup_random_event(green_templates,
                           event_datetime,
                           [random.choice(green_equipment)._id],
                           [random.choice(everybody)._id],
                           verbose=True)


    show_current_events()
    show_coming_events()

    show_all_machine_status()

    write_mail_aliases(all_types)

if __name__ == "__main__":
    main()
