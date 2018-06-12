from nevow import flat
from nevow import tags as T
import equipment_type
import event
import person
import timeline
import timeslots
import datetime

def responsibilities(who, typename, keyed_types):
    is_owner = who.is_owner(keyed_types[typename])
    is_trainer = who.is_trainer(keyed_types[typename])
    return [T.dl[T.dt["Owner"
                      if is_owner
                      else "Not yet an owner"],
                 T.dd[((T.a(href="schedmaint?type=%s"%typename, class_="button")["Schedule maintenance"])
                       if is_owner
                       else ((T.a(href="request?type=%s&role=owner"%typename,
                                  class_="button")["Request owner training"])
                             if not who.has_requested_training([keyed_types[typename]._id], 'owner')
                             else (T.a(href="canreq?type=%s&role=owner"%typename,
                                       class_="negbutton")["Cancel owner training request"])))],
                 T.dt["Trainer"
                      if is_trainer
                      else "Not yet a trainer"],
                 T.dd[((T.a(href="schedtrain?type=%s"%typename, class_="button")["Schedule training"])
                       if is_trainer
                       else (T.a(href="request?type=%s&role=trainer"%typename,
                                 class_="button")["Request owner training"]
                             if not who.has_requested_training([keyed_types[typename]._id], 'owner')
                             else T.a(href="canreq?type=%s&role=trainer"%typename,
                                      class_="negbutton")["Cancel owner training request"]))]]]

def availform(available):
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
              T.input(type="submit", value="Update")]])

def eventlist(evlist):
    return T.dl[[[T.dt[event.Event.timestring(ev.start)],
                  T.dd[ev.event_type # todo: add title, hosts if allowed, attendees if allowed, etc
                  ]] for ev in evlist]]

def person_page_contents(who, viewer):
    days, _, times = timeslots.get_slots_conf()
    result = [T.h2["Personal details"],
              T.div(class_="personaldetails")[
                  T.table(class_="personaldetails")[
                      T.tr[T.th["Name"], T.td[who.name()]],
                      T.tr[T.th["email"], T.td[who.get_email()]],
                      T.tr[T.th["Membership number"], T.td[str(who.membership_number)]],
                      T.tr[T.th["link-id"], T.td[str(who.link_id)]],
                      T.tr[T.th[""], T.td["address etc to go here"]]],
                  T.h2["Availability"],
                  availform(who.available)]]
    their_responsible_types = set(who.get_equipment_types('owner') + who.get_equipment_types('trainer'))
    if len(their_responsible_types) > 0:
        keyed_types = { ty.name.replace('_', ' ').capitalize(): ty for ty in their_responsible_types }
        result += [T.h2["Equipment responsibilities"],
                   T.div(class_="resps")[T.dl[T.dt[name],
                                              T.dd[responsibilities(who, name, keyed_types)]
                                                for name in sorted(keyed_types.keys())]]]
    their_equipment_types = set(who.get_equipment_types('user')) - their_responsible_types
    if len(their_equipment_types) > 0:
        keyed_types = { ty.name.replace('_', ' ').capitalize(): ty for ty in their_equipment_types }
        result += [T.h2["Equipment trained on"],
                   T.div(class_="trainedon")[
                       # todo: add owner/trainer training request/cancel buttons
                       T.ul[[T.li[name] for name in sorted(keyed_types.keys())]]]]
    all_remaining_types = ((set(equipment_type.Equipment_type.list_equipment_types())
                            -their_responsible_types)
                           -their_equipment_types)
    if len(all_remaining_types) > 0:
        result += [T.h2["Other equipment"],
                   T.dl[[T.dt[eqty.name].replace('_', ' ').capitalize(),
                       T.dd[T.a(href="request?type=%s&role=user"%eqty.name,
                                class_="button")["Request training"]
                           if not who.has_requested_training(eqty._id, 'user')
                           else T.a(href="canreq?type=%s&role=user"%eqty.name,
                                    class_="button")["Cancel training request"]]]
                        for eqty in all_remaining_types]]
    if len(who.training_requests) > 0:
        len_training = len("_training")
        keyed_requests = { req['request_date']: req for req in who.training_requests }
        sorted_requests = [keyed_requests[k] for k in sorted(keyed_requests.keys()) ]
        result += [T.h2["Training requests"],
               T.div(class_="requested")[T.table()[T.tr[T.th["Date"],T.th["Equipment"],T.th["Role"]],
                                                   [T.tr[T.td[req['request_date'].strftime("%Y-%m-%d")],
                                                         T.td[", ".join([equipment_type.Equipment_type.find_by_id(id).name.replace('_', ' ').capitalize()
                                                                         for id in req['equipment_types']])],
                                                         T.td[str(req['event_type'])[:-len_training]]]
                                                    for req in sorted_requests]]]]

    known_events = []

    hosting = timeline.Timeline.future_events(person_field='hosts', person_id=who._id).events

    if len(hosting) > 0:
        result += [T.h2["Events I'm hosting"],
                   T.div(class_="hostingevents")[
                       eventlist(hosting)]]

    result += [T.h2["Events signed up for"],
               T.div(class_="signedevents")[
                   "todo: list of events signed up for to go here"
               ],
            T.h2["Events I can sign up for"],
               T.div(class_="availableevents")[
                   "todo: list of available events to go here"
               ],
            T.h2["API links"],
               T.div(class_="apilinks")[
                   "todo: api links to go here"
               ]]
    return result
