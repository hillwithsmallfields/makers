from nevow import flat
from nevow import tags as T
import equipment_type
import event
import person
import timeline
import timeslots
import datetime

def machinelist(eqty, who, as_owner=False):
    """Make a list of machines, with appropriate detail for each."""
    return [T.dl[[[T.dt[machine.name],
                  T.dd[T.dl[T.dt["Status"], T.dd[machine.status],
                            [T.dt["Schedule maintenance"],
                             T.dd[T.form(action="schedmaint")[T.input(type="datetime", name="when"),
                                                              T.input(type="hidden", name="type", value=eqty.name),
                                                              T.input(type="hidden", name="submitter", value=who._id),
                                           T.input(type="submit", value="Schedule")]]]
                            if as_owner else []]]]
                  for machine in eqty.get_machines()]]]

def responsibilities(who, typename, keyed_types):
    is_owner = who.is_owner(keyed_types[typename])
    is_trainer = who.is_trainer(keyed_types[typename])
    return [T.dl[T.dt["Machines"],
                 T.dd[machinelist(equipment_type.Equipment_type.find(typename),
                                  who, is_owner)],
                 T.dt["Owner"
                      if is_owner
                      else "Not yet an owner"],
                 T.dd[(T.form(action="schedtrain")[T.input(type="datetime", name="when"),
                                                    T.input(type="hidden", name="role", value="Owner training"),
                                                    T.input(type="hidden", name="type", value=typename),
                                                    T.input(type="hidden", name="submitter", value=who._id),
                                                    T.input(type="submit", value="Schedule owner training")]
                       if is_owner
                       else ((T.a(href="request?type=%s&role=owner"%typename,
                                  class_="button")["Request owner training"])
                             if not who.has_requested_training([keyed_types[typename]._id], 'owner')
                             else (T.a(href="canreq?type=%s&role=owner"%typename,
                                       class_="negbutton")["Cancel owner training request"])))],
                 T.dt["Trainer"
                      if is_trainer
                      else "Not yet a trainer"],
                 T.dd[((T.form(action="schedtrain")[T.input(type="datetime", name="when"),
                                                    T.input(type="radio", name="role", value="User training"),
                                                    T.input(type="radio", name="role", value="Trainer training"),
                                                    T.input(type="hidden", name="type", value=typename),
                                                    T.input(type="hidden", name="submitter", value=who._id),
                                                    T.input(type="submit", value="Schedule training")]
                       if is_trainer
                       else (T.a(href="request?type=%s&role=trainer"%typename,
                                 class_="button")["Request trainer training"]
                             if not who.has_requested_training([keyed_types[typename]._id], 'trainer')
                             else T.a(href="canreq?type=%s&role=trainer"%typename,
                                      class_="negbutton")["Cancel trainer training request"]))]]]

def availform(available):
    days, _, times = timeslots.get_slots_conf()
    return (T.div(class_="availability")
            [T.form(action="updateavail")
             [T.table(class_="availability")
              [T.tr[T.th(class_="daylabel")["Day"],
                    T.th["Morning"],
                    T.th["Afternoon"],
                    T.th["Evening"],
                    T.th["Other"]],
               [[T.tr[T.th(class_="daylabel")[day],
                      [T.td[T.input(type="checkbox", name="avail",
                                    value=day+t, checked="checked")
                            if b
                            else T.input(type="checkbox", name="avail",
                                         value=day+t)]
                       for t, b in zip(['M', 'A', 'E', 'O'], day_slots)]]]
                for (day, day_slots) in zip(days,
                                            timeslots.timeslots_from_int(available))]],
              T.input(type="submit", value="Update availability")]])

def eventlist(evlist, with_signup=False):
    return T.dl[[[T.dt[event.timestring(ev.start)],
                  T.dd[ev.event_type,
                       T.a(href="signup?id=%s"%ev._id,
                           class_="button")["Sign up"]
                       # todo: add title, hosts if allowed, attendees if allowed, etc, and signup button
                  ]] for ev in evlist]]

def person_page_contents(who, viewer):
    result = [T.h2["Personal details"],
              T.div(class_="personaldetails")[
                  T.form(action="updatedetails")[T.table(class_="personaldetails")[
                      T.tr[T.th["Name"], T.td[T.input(type="text", value=who.name())]],
                      T.tr[T.th["email"], T.td[T.input(type="email", value=who.get_email())]],
                      T.tr[T.th["Membership number"], T.td[str(who.membership_number)]],
                      T.tr[T.th["link-id"], T.td[str(who.link_id)]],
                      T.tr[T.th[""], T.td["address etc to go here"]]],
                                                 T.input(type="submit", value="Update details")],
                  T.h2["Availability"],
                  availform(who.available)]]
    their_responsible_types = set(who.get_equipment_types('owner') + who.get_equipment_types('trainer'))
    if len(their_responsible_types) > 0:
        keyed_types = { ty.name.replace('_', ' ').capitalize(): ty for ty in their_responsible_types }
        result += [T.h2["Equipment responsibilities"],
                   T.div(class_="resps")[T.dl[[[T.dt[name],
                                               T.dd[responsibilities(who, name, keyed_types)]]
                                               for name in sorted(keyed_types.keys())]]]]
    their_equipment_types = set(who.get_equipment_types('user')) - their_responsible_types
    if len(their_equipment_types) > 0:
        keyed_types = { ty.name.replace('_', ' ').capitalize(): ty for ty in their_equipment_types }
        result += [T.h2["Equipment trained on"],
                   T.div(class_="trainedon")[
                       T.dl[[[T.dt[name],
                              T.dd[T.a(href="request?type=%s&role=trainer"%eqty.name,
                                       class_="button")["Request trainer training"]
                               if not who.has_requested_training([eqty._id], 'trainer')
                               else T.a(href="canreq?type=%s&role=user"%eqty.name,
                                        class_="negbutton")["Cancel trainer training request"],
                                   T.a(href="request?type=%s&role=owner"%eqty.name,
                                       class_="button")["Request owner training"]
                               if not who.has_requested_training([eqty._id], 'owner')
                               else T.a(href="canreq?type=%s&role=owner"%eqty.name,
                                        class_="negbutton")["Cancel owner training request"]]]
                             for name in sorted(keyed_types.keys())]]]]
    all_remaining_types = ((set(equipment_type.Equipment_type.list_equipment_types())
                            -their_responsible_types)
                           -their_equipment_types)
    if len(all_remaining_types) > 0:
        result += [T.h2["Other equipment"],
                   T.dl[[[T.dt[eqty.name.replace('_', ' ').capitalize()],
                          T.dd[T.a(href="request?type=%s&role=user"%eqty.name,
                                   class_="button")["Request training"]
                               if not who.has_requested_training([eqty._id], 'user')
                               else T.a(href="canreq?type=%s&role=user"%eqty.name,
                                        class_="negbutton")["Cancel training request"]]]
                         for eqty in all_remaining_types]]]
    if len(who.training_requests) > 0:
        len_training = len("_training")
        keyed_requests = { req['request_date']: req for req in who.training_requests }
        sorted_requests = [keyed_requests[k] for k in sorted(keyed_requests.keys()) ]
        result += [T.h2["Training requests"],
               T.div(class_="requested")[T.table()[T.tr[T.th["Date"],T.th["Equipment"],T.th["Role"]],
                                                   [T.tr[T.td[req['request_date'].strftime("%Y-%m-%d")],
                                                         T.td[", ".join([equipment_type.Equipment_type.find_by_id(id).name.replace('_', ' ').capitalize()
                                                                         for id in req['equipment_types']])],
                                                         T.td[str(req['event_type'])[:-len_training]],
                                                         T.a(href="canreq?type=%s&role=user"%".".join(req['equipment_types']),
                                                             class_="negbutton")["Cancel training request"]]
                                                    for req in sorted_requests]]]]

    hosting = timeline.Timeline.future_events(person_field='hosts', person_id=who._id).events

    if len(hosting) > 0:
        result += [T.h2["Events I'm hosting"],
                   T.div(class_="hostingevents")[eventlist(hosting)]]

    attending = timeline.Timeline.future_events(person_field='attendees', person_id=who._id).events

    if len(attending) > 0:
        result += [T.h2["Events I'm attending"],
                   T.div(class_="attendingingevents")[eventlist(attending)]]

    hosted = timeline.Timeline.past_events(person_field='hosts', person_id=who._id).events

    if len(hosting) > 0:
        result += [T.h2["Events I have hosted"],
                   T.div(class_="hostedevents")[eventlist(hosted)]]

    attended = timeline.Timeline.past_events(person_field='attendees', person_id=who._id).events

    if len(attended) > 0:
        result += [T.h2["Events I have attended"],
                   T.div(class_="attendedingevents")[eventlist(attended)]]

    known_events = hosting + attending + hosted + attended

    available_events = [ev
                        for ev in timeline.Timeline.future_events()
                        if ev not in known_events]

    if len(available_events) > 0:
        result += [T.h2["Events I can sign up for"],
                   T.div(class_="availableevents")[eventlist(availableevents, True)]]

    if who.is_administrator() or who.is_auditor():
            result += [T.h2(class_="admin")["Admin actions"],
                       T.ul[T.li[T.a(href="userlist", class_="adminbutton")["User list"]],
                            T.li[T.a(href="intervene", class_="adminbutton")["Intervention (special event)"]]
                            if who.is_administrator() else ""]]

    result += [T.h2["API links"],
               T.div(class_="apilinks")[
                   "todo: api links to go here"
               ]]
    return result
