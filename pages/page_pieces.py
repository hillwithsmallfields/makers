from nevow import flat
from nevow import tags as T
import configuration
import equipment_type
import event
import person
import timeline
import timeslots
import datetime

"""Assorted useful bits of stan expressions for constructing our pages."""

server_conf = None

def set_server_conf():
    global server_conf
    server_conf = configuration.get_config()['server']

def section_link(section, name, presentation):
    return T.a(href=server_conf['base_url']+server_conf[section]+name)[presentation]

def machine_link(name):
    return section_link('machines', name, name)

def request_button(typename, role, button_text):
    return T.form(action=server_conf['base_url']+"request",
                  method='POST')[T.input(type="hidden", name="typename", value=typename),
                                 T.input(type="hidden", name="role", value=role),
                                 T.button(type="submit", value="request")[button_text]]

def cancel_button(typename, role, button_text):
    return T.form(action=server_conf['base_url']+"cancel_request",
                  method='POST')[T.input(type="hidden", name="typename", value=typename),
                                 T.input(type="hidden", name="role", value=role),
                                 T.button(type="submit", value="cancel_request")[button_text]]

def toggle_request(name, role, already_requested):
    return (request_button(name, 'trainer', "Request %s training"%role)
            if not already_requested
            else cancel_button(name, 'trainer', "Cancel %s training request"%role))

def signup_button(event_id, button_text):
    return T.form(action=server_conf['base_url']+"signup",
                  method='POST')[T.input(type="hidden", name="eventid", value=str(event_id)),
                                 T.button(type="submit", value="cancel_request")[button_text]]

def schedule_event_form(who, extras, button_text):
    return (T.form(action=server_conf['base_url']+"schedevent",
                   method='POST')
            ["Date and time: ", T.input(type="datetime", name="when"), T.br,
             extras,
             T.input(type="hidden", name="submitter", value=str(who._id)),
             T.button(type="submit", value="schedule")[button_text]])

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

def machinelist(eqty, who, as_owner=False):
    """Make a list of machines, with appropriate detail for each."""
    # todo: this, or something underneath it, isn't working
    if eqty is None:
        return []
    mclist = eqty.get_machines()
    return ([T.dl[[[T.dt[machine_link(machine.name)],
                    T.dd[T.dl[T.dt["Status"], T.dd[machine.status],
                              [T.dt["Schedule maintenance"],
                               T.dd[schedule_event_form(who,
                                                        [T.input(type="hidden", name="machine", value=machine.name),
                                                         T.input(type="hidden", name="event_type", value="maintenance")],
                                                        "Schedule maintenance")]]
                              if as_owner else []]]]
                   for machine in mclist]]]
            if mclist
            else [])

def eventlist(evlist, with_signup=False):
    return T.dl[[[T.dt[event.timestring(ev.start)],
                  T.dd[T.a(href=server_conf['base_url']+server_conf['events']+str(ev._id))[ev.title or "Untitled"],
                       " ",
                       ev.event_type,
                       " on ",
                       ", ".join([equipment_type.Equipment_type.find(e).name for e in ev.equipment_types]),
                       signup_button(ev._id, "Sign up") if with_signup else ""
                       # todo: add title, hosts if allowed, attendees
                  ]] for ev in evlist]]