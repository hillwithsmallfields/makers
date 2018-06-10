from nevow import flat
from nevow import tags as T
import equipment_type
import person
import timeslots
import datetime

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
                  T.div(class_="availability")[
                      T.form(action="updateavail") [
                          T.table(class_="availability")[
                              T.tr[T.th["Day"], T.th["Morning"], T.th["Afternoon"], T.th["Evening"], T.th["Other"]],
                              [ [ T.tr [ T.th[day], [
                                  T.td[T.input(type="checkbox", name="avail",
                                               value=day+t, checked="checked")
                                       if b else
                                       T.input(type="checkbox", name="avail",
                                               value=day+t)]
                                  for t, b in zip(['M', 'A', 'E', 'O'], day_slots) ] ] ]
                                for (day, day_slots) in zip(days, timeslots.timeslots_from_int(who.available)) ]],
                          T.input(type="submit", value="Update")]]]]
    all_remaining_types = set(equipment_type.Equipment_type.list_equipment_types())
    their_responsible_types = set(who.get_equipment_types('owner') + who.get_equipment_types('trainer'))
    if len(their_responsible_types) > 0:
        keyed_types = { ty.name.replace('_', ' ').capitalize(): ty for ty in their_responsible_types }
        result += [T.h2["Equipment responsibilities"],
                   T.div(class_="resps")[T.ul[[ T.li[name,
                                                     # todo: make these a description list within the list item
                                                     ((T.a(href="createmaint", class_="button")["Schedule maintenance"])
                                                      if who.is_owner(keyed_types[name])
                                                      else (
                                                              # todo: or cancel training if already requested
                                                              T.a(href="requestOT")["Request owner training"])),
                                                     ((T.a(href="schedtrain", class_="button")["Schedule training"])
                                                      if who.is_trainer(keyed_types[name])
                                                      else (
                                                              # todo: or cancel training if already requested
                                                              T.a(href="requestTT", class_="button")["Request owner training"]))]
                                                for name in sorted(keyed_types.keys())]]]]
    their_equipment_types = set(who.get_equipment_types('user')) - their_responsible_types
    if len(their_equipment_types) > 0:
        keyed_types = { ty.name.replace('_', ' ').capitalize(): ty for ty in their_equipment_types }
        result += [T.h2["Equipment trained on"],
                   T.div(class_="trainedon")[
                       T.ul[[T.li[name] for name in sorted(keyed_types.keys())]]]]
    if len(who.training_requests) > 0:
        result += [T.h2["Training requests"],
               T.div(class_="requested")[
                   T.table()[T.tr[T.th["Date"],T.th["Equipment"],T.th["Role"]],
                             [T.tr[T.td[req['request_date'].strftime("%Y-%m-%d")],
                                   T.td[", ".join([ equipment_type.Equipment_type.find_by_id(id).name for id in req['equipment_types']])],
                                   T.td[str(req['event_type'])] # todo: convert to role
                               ] for req in who.training_requests # todo: sort by date
                          ],
                         ]
               ]]
    result += [T.h2["Events I'm hosting"],
               T.div(class_="hostingevents")[
                   "todo: list of events they're hosting to go here"
               ],
            T.h2["Events signed up for"],
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
