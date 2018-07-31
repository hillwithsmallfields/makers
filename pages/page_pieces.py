from untemplate.throw_out_your_templates_p3 import htmltags as T
import django.urls
import model.configuration
import model.equipment_type
import model.event
import model.machine
import model.person
import model.timeline
import model.timeslots
import datetime

"""Assorted useful bits of expressions for constructing our pages."""

server_conf = None

def set_server_conf():
    global server_conf
    server_conf = model.configuration.get_config()['server']

def top_navigation(django_request):
    org_conf = model.configuration.get_config()['organization']
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST'] + "/"
    # todo: make this a bar of buttons, or a dropdow
    return [T.nav(class_='top_nav')
            [T.ul[T.li[T.a(href=org_conf['home_page'])[org_conf['title'] + " home"]],
                  T.li[T.a(href=org_conf['wiki'])["Wiki"]],
                  T.li[T.a(href=org_conf['forum'])["Forum"]],
                  T.li[T.a(href=base + "dashboard/")["Your dashboard"]],
                  T.li[T.a(href=base + 'users/logout')["Logout"]]]]]

# https://stackoverflow.com/questions/2345708/how-can-i-get-the-full-absolute-url-with-domain-in-django
# request.build_absolute_url()
# https://docs.djangoproject.com/en/2.0/topics/http/urls/
# https://docs.djangoproject.com/en/2.0/ref/urlresolvers/

def section_link(section, name, presentation):
    return T.a(href=django.urls.reverse(section, args=[name]))[presentation]

def machine_link(name):
    return section_link('machines:index', name, name)

def request_button(who, eqty_id, role, button_text, django_request):
    return T.form(action=django.urls.reverse("training:request"),
                  method='POST')[T.input(type="hidden", name="equiptype", value=eqty_id),
                                 T.input(type="hidden", name="role", value=role),
                                 T.input(type="hidden", name="person", value=who._id),
                                 T.input(type="hidden", name="csrfmiddlewaretoken", value=django.middleware.csrf.get_token(django_request)),
                                 T.button(type="submit", value="request")[button_text]]

def cancel_button(who, eqty_id, role, button_text, django_request):
    return T.form(action=django.urls.reverse("training:cancel"),
                  method='POST')[T.input(type="hidden", name="equiptype", value=eqty_id),
                                 T.input(type="hidden", name="role", value=role),
                                 T.input(type="hidden", name="person", value=who._id),
                                 T.input(type="hidden", name="csrfmiddlewaretoken", value=django.middleware.csrf.get_token(django_request)),
                                 T.button(type="submit", value="cancel_request")[button_text]]

def toggle_request(who, eqty, role, already_requested, django_request):
    return (request_button(who, eqty, role, "Request %s training"%role, django_request)
            if not already_requested
            else cancel_button(who, eqty, role, "Cancel %s training request"%role, django_request))

def signup_button(event_id, who_id, button_text, django_request):
    return T.form(action=server_conf['base_url']+"signup",
                  method='POST')[T.input(type="hidden", name="eventid", value=str(event_id)),
                                 T.input(type="hidden", name="person_id", value=who_id),
                                 T.input(type="hidden", name="csrfmiddlewaretoken", value=django.middleware.csrf.get_token(django_request)),
                                 T.button(type="submit", value="cancel_request")[button_text]]

def schedule_event_form(who, extras, button_text, django_request):
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST'] + "/"
    return (T.form(action=base+django.urls.reverse("events:newevent"),
                   method='POST')
            ["Date and time: ", T.input(type="datetime", name="when"), T.br,
             extras,
             T.input(type="hidden", name="submitter", value=str(who._id)),
             T.input(type="hidden", name="csrfmiddlewaretoken", value=django.middleware.csrf.get_token(django_request)),
             T.button(type="submit", value="schedule")[button_text]])

def availform(available, django_request):
    days, _, times = model.timeslots.get_slots_conf()
    return (T.div(class_="availability")
            [T.form(action="updateavail",
                    method="POST")
             [T.table(class_="availability")
              [[T.thead[T.tr[T.th(class_="daylabel")["Day"],
                             T.th["Morning"],
                             T.th["Afternoon"],
                             T.th["Evening"],
                             T.th["Other"]]]],
               T.tbody[[[T.tr[T.th(class_="daylabel")[day],
                              [T.td[T.input(type="checkbox", name="avail",
                                            value=day+t, checked="checked")
                                    if b
                                    else T.input(type="checkbox", name="avail",
                                                 value=day+t)]
                               for t, b in zip(['M', 'A', 'E', 'O'], day_slots)]]]
                        for (day, day_slots) in zip(days,
                                                    model.timeslots.timeslots_from_int(available))]]]],
             # todo: write receiver for this
             # todo: on changing availability, re-run invite_available_interested_people on the equipment types for which this person has a training request outstanding
             T.input(type="hidden", name="csrfmiddlewaretoken", value=django.middleware.csrf.get_token(django_request)),
             T.input(type="submit", value="Update availability")])

def avail_table(slot_sums):
    days, _, _ = model.timeslots.get_slots_conf()
    return [T.table(class_="availability")
            [T.thead[T.tr[T.th(class_="daylabel")["Day"],
                          T.th["Morning"],
                          T.th["Afternoon"],
                          T.th["Evening"],
                          T.th["Other"]]]],
            T.tbody[[[T.tr[T.th(class_="daylabel")[day],
                           [T.td[str(b)]
                       for t, b in zip(['M', 'A', 'E', 'O'], day_slots)]]]
                for (day, day_slots) in zip(days,
                                            model.timeslots.avsums_by_day(slot_sums))]]]

def general_equipment_list(who, viewer, these_types, django_request, detailed=False):
    keyed_types = {eqty.name: eqty for eqty in these_types}
    return T.table[T.thead[T.tr[T.th["Equipment type"], T.th["Request"], T.th["Admin action"] if viewer.is_administrator() else ""]],
                   T.tbody[[[T.tr[T.th[T.a(href=server_conf['base_url']+server_conf['types']+name)[name.replace('_', ' ').capitalize()]],
                                  T.td[machinelist(keyed_types[name],
                                                   who, django_request, False) if detailed else "",
                                       toggle_request(who, keyed_types[name]._id, 'user',
                                                      who.has_requested_training([keyed_types[name]._id], 'user'),
                                                      django_request)],
                                  T.td[permit_form(keyed_types[name], who, 'user')] if viewer.is_administrator() else ""]]
                            for name in sorted(keyed_types.keys())]]]

def machinelist(eqty, who, django_request, as_owner=False):
    """Make a list of machines, with appropriate detail for each."""
    if eqty is None:
        return []
    mclist = eqty.get_machines()
    return ([T.table[T.thead[T.tr[T.th["Machine"], T.th["Status"], T.th["Owner actions" if as_owner else ""]]],
                     T.tbody[[[T.tr[T.th[machine_link(device.name)],
                                    T.td[device.status],
                                    T.td[schedule_event_form(who,
                                                             [T.input(type="hidden", name="machine", value=device.name),
                                                              T.input(type="hidden", name="event_type", value="maintenance")],
                                                             "Schedule maintenance",
                                                             django_request)
                                 if as_owner else ""]]]
                              for device in mclist]]]]
            if mclist
            else [])

def eqty_training_requests(eqtype):
    raw_reqs = eqtype.get_training_requests()
    print("raw_reqs is", raw_reqs)
    reqs = []
    # we can't use dates as dictionary keys, as they might not be
    # unique, so go through all the dates in order getting all
    # requests which have that date, so they will be in order
    for d in sorted([req['request_date'] for req in raw_reqs]):
        for r in raw_reqs:
            if r['request_date'] == d:
                reqs.append(r)
    print("reqs are", reqs)
    return [T.table[T.thead[T.tr[T.th["Date requested"],
                                T.th["Requester"]]],
                   T.tbody[[[T.tr[T.td[event.timestring(req['request_date'])],
                                 T.td[person.Person.find(req['requester']).name()]]]
                            for req in reqs]]],
            avail_table(timeslots.sum_availabilities([person.Person.find(req['requester']).available
                                                      for req in raw_reqs]))]

def special_event_form(eqtype, who_id, role, enable, css_class, duration_label, button_label):
    return T.form(action="events/special",
                  class_=css_class,
                  method='POST')[button_label,
                                 T.input(type='hidden', name='eqtype', value=eqtype._id),
                                 T.input(type='hidden', name='who', value=who_id),
                                 T.input(type='hidden', name='role', value=role),
                                 T.input(type='hidden', name='enable', value=enable),
                                 duration_label, T.input(type='text', name='duration'),
                                 T.input(type='submit', value=button_label)]

def permit_form(eqtype, who_id, role):
    return special_event_form(eqtype, who_id, role, 'True', "permit_form", "Duration in days (blank for indefinite): ", 'Grant permission')

def ban_form(eqtype, who_id, role):
    return special_event_form(eqtype, who_id, role, 'False', "ban_form", "Duration in days (blank for indefinite): ", 'Ban')

def announcements_section():
    return T.div[T.p["Placeholder."]]
