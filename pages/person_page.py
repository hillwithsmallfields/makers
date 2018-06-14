from nevow import flat
from nevow import tags as T
import configuration
import equipment_type
import event
import page_pieces
import person
import timeline
import timeslots
import datetime

server_conf = None

def responsibilities(who, typename, keyed_types):
    is_owner = who.is_owner(keyed_types[typename])
    has_requested_owner_training = who.has_requested_training([keyed_types[typename]._id], 'owner')
    is_trainer = who.is_trainer(keyed_types[typename])
    has_requested_trainer_training = who.has_requested_training([keyed_types[typename]._id], 'trainer')
    return [T.dl[T.dt["Machines"],
                 T.dd[page_pieces.machinelist(equipment_type.Equipment_type.find(typename),
                                              who, is_owner)],
                 T.dt["Owner"
                      if is_owner
                      else "Not yet an owner"+(" but has requested owner training" if has_requested_owner_training else "")],
                 T.dd[(page_pieces.schedule_event_form(who, [T.input(type="hidden", name="event_type", value="training"),
                                                             T.input(type="hidden", name="role", value="owner"),
                                                             T.input(type="hidden", name="type", value=typename)],
                                                       "Schedule owner training")
                       if is_owner
                       else page_pieces.toggle_request(typename, 'owner',
                                                       has_requested_owner_training))],
                 T.dt["Trainer"
                      if is_trainer
                      else "Not yet a trainer"+(" but has requested trainer training" if has_requested_trainer_training else "")],
                 T.dd[(page_pieces.schedule_event_form(who, [T.input(type="hidden", name="event_type", value="training"),
                                                             "User training: ", T.input(type="radio",
                                                                                        name="role",
                                                                                        value="user",
                                                                                        checked="checked"), T.br,
                                                             "Trainer training: ", T.input(type="radio",
                                                                                           name="role",
                                                                                           value="trainer"), T.br,
                                                             T.input(type="hidden", name="type", value=typename),
                                                             T.input(type="hidden", name="type", value=typename)],
                                                       "Schedule training")
                       if is_trainer
                       else page_pieces.toggle_request(typename, 'trainer',
                                                       has_requested_trainer_training))]]]

def person_page_contents(who, viewer):
    global server_conf
    server_conf = configuration.get_config()['server']
    page_pieces.set_server_conf()
    result = [T.h2["Personal profile"],
              T.div(class_="personalprofile")[
                  T.form(action="updateprofile",
                         method='POST')[T.table(class_="personaldetails")[
                             T.tr[T.th(class_="ralabel")["Name"], T.td[T.input(type="text",
                                                                               name="name",
                                                                               value=who.name())]],
                             T.tr[T.th(class_="ralabel")["email"], T.td[T.input(type="email",
                                                                                name="email",
                                                                                value=who.get_email())]],
                             T.tr[T.th(class_="ralabel")["Membership number"], T.td[str(who.membership_number)]],
                             T.tr[T.th(class_="ralabel")['Fob number'],
                                  T.td[(T.input(type="text",
                                                name="fob",
                                                value=str(who.fob))
                                        if viewer.is_administrator()
                                        else [str(who.fob)])]],
                             T.tr[T.th(class_="ralabel")["link-id"], T.td[str(who.link_id)]],
                             T.tr[T.th(class_="ralabel")[""], T.td["address etc to go here"]]],
                                        T.input(type="submit", value="Update details")],
                  T.h2["Availability"],
                  page_pieces.availform(who.available)]]
    their_responsible_types = set(who.get_equipment_types('owner') + who.get_equipment_types('trainer'))
    if len(their_responsible_types) > 0:
        keyed_types = { ty.name.replace('_', ' ').capitalize(): ty for ty in their_responsible_types }
        result += [T.h2["Equipment responsibilities"],
                   T.div(class_="resps")[T.dl[[[T.dt[T.a(href=server_conf['base_url']+server_conf['types']+keyed_types[name].name)[name]],
                                                T.dd[responsibilities(who, name, keyed_types)]]
                                               for name in sorted(keyed_types.keys())]]]]
    their_equipment_types = set(who.get_equipment_types('user')) - their_responsible_types
    if len(their_equipment_types) > 0:
        keyed_types = { ty.name.replace('_', ' ').capitalize(): (ty,
                                                                 who.qualification(ty.name, 'user'))
                        for ty in their_equipment_types }
        result += [T.h2["Equipment trained on"],
                   T.div(class_="trainedon")[
                       T.dl[[[T.dt[T.a(href=server_conf['base_url']+server_conf['types']+name)[name]],
                              T.dd[ # todo: add when they were trained, and by whom
                                  "Since ", event.timestring(keyed_types[name][1].start), T.br,
                                  page_pieces.toggle_request(name, 'trainer',
                                                             who.has_requested_training([keyed_types[name][0]._id], 'trainer')),
                                  page_pieces.toggle_request(name, 'owner',
                                                             who.has_requested_training([keyed_types[name][0]._id], 'owner')),
                                  page_pieces.machinelist(keyed_types[name],
                                                          who, False)]]
                             for name in sorted(keyed_types.keys())]]]]
    all_remaining_types = ((set(equipment_type.Equipment_type.list_equipment_types())
                            -their_responsible_types)
                           -their_equipment_types)
    if len(all_remaining_types) > 0:
        keyed_types = {eqty.name: eqty for eqty in all_remaining_types}
        result += [T.h2["Other equipment"],
                   T.dl[[[T.dt[T.a(href=server_conf['base_url']+server_conf['types']+name)[name.replace('_', ' ').capitalize()]],
                          T.dd[page_pieces.machinelist(keyed_types[name],
                                                       who, False),
                               page_pieces.toggle_request(name, 'user', who.has_requested_training([keyed_types[name]._id], 'user'))]]
                         for name in sorted(keyed_types.keys())]]]
    if len(who.training_requests) > 0:
        len_training = len("_training")
        keyed_requests = {req['request_date']: req for req in who.training_requests}
        sorted_requests = [keyed_requests[k] for k in sorted(keyed_requests.keys())]
        result += [T.h2["Training requests"],
                   T.div(class_="requested")[T.table()[T.tr[T.th["Date"],T.th["Equipment"],T.th["Role"]],
                                                       [T.tr[T.td[req['request_date'].strftime("%Y-%m-%d")],
                                                             T.td[", ".join([equipment_type.Equipment_type.find_by_id(id).name.replace('_', ' ').capitalize()
                                                                             for id in req['equipment_types']])],
                                                             T.td[str(req['event_type'])[:-len_training]],
                                                             T.td[page_pieces.cancel_button(",".join(map(str, req['equipment_types'])),
                                                                                            'user', "Cancel training request")]]
                                                        for req in sorted_requests]]]]

    hosting = timeline.Timeline.future_events(person_field='hosts', person_id=who._id).events

    if len(hosting) > 0:
        result += [T.h2["Events I'm hosting"],
                   T.div(class_="hostingevents")[page_pieces.eventlist(hosting)]]

    attending = timeline.Timeline.future_events(person_field='attendees', person_id=who._id).events

    if len(attending) > 0:
        result += [T.h2["Events I'm attending"],
                   T.div(class_="attendingingevents")[page_pieces.eventlist(attending)]]

    hosted = timeline.Timeline.past_events(person_field='hosts', person_id=who._id).events

    if len(hosting) > 0:
        result += [T.h2["Events I have hosted"],
                   T.div(class_="hostedevents")[page_pieces.eventlist(hosted)]]

    attended = timeline.Timeline.past_events(person_field='attendees', person_id=who._id).events

    if len(attended) > 0:
        result += [T.h2["Events I have attended"],
                   T.div(class_="attendedingevents")[page_pieces.eventlist(attended)]]

    known_events = hosting + attending + hosted + attended

    available_events = [ev
                        for ev in timeline.Timeline.future_events().events
                        if ev not in known_events]

    if len(available_events) > 0:
        result += [T.h2["Events I can sign up for"],
                   T.div(class_="availableevents")[page_pieces.eventlist(available_events, True)]]

    if viewer.is_administrator() or viewer.is_auditor():
        result += [T.h2(class_="admin")["Admin actions"],
                   T.ul[T.li[page_pieces.section_link('admin', "userlist", "User list")],
                        T.li[page_pieces.section_link('admin', "intervene", "Create intervention event")]
                        if who.is_administrator() else ""]]

    userapilink = page_pieces.section_link("userapi", who.link_id, who.link_id)
    api_link = ["Your user API link is ", T.a(href=userapilink)[userapilink]]
    if who.api_authorization is None:
        api_link += [T.br,
                     "You will need to register to get API access authorization.",
                     T.form(action=server_conf['base_url']+server_conf['userapi']+"authorize",
                            method='POST')[T.button(type="submit", value="authorize")["Get API authorization code"]]]
    result += [T.h2["API links"],
               T.div(class_="apilinks")[api_link]]

    return result
