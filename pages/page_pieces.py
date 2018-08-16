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
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST']
    # todo: make this a bar of buttons, or a dropdow
    return [T.nav(class_='top_nav')
            [T.ul[T.li[T.a(href=org_conf['home_page'])[org_conf['title'] + " home"]],
                  T.li[T.a(href=org_conf['wiki'])["Wiki"]],
                  T.li[T.a(href=org_conf['forum'])["Forum"]],
                  T.li[T.a(href=base + "/dashboard/")["Your dashboard"]],
                  T.li[T.a(href=base + '/users/logout')["Logout"]]]]]

# https://stackoverflow.com/questions/2345708/how-can-i-get-the-full-absolute-url-with-domain-in-django
# request.build_absolute_url()
# https://docs.djangoproject.com/en/2.0/topics/http/urls/
# https://docs.djangoproject.com/en/2.0/ref/urlresolvers/

def section_link(section, name, presentation):
    return T.a(href=django.urls.reverse(section, args=[name]))[presentation]

def machine_link(name):
    return section_link('machines:index', name, name)

def request_button(who, eqty_id, role, button_text, django_request):
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST']
    return T.form(action=base+django.urls.reverse("training:request"),
                  method='POST')[T.input(type="hidden", name="equiptype", value=eqty_id),
                                 T.input(type="hidden", name="role", value=role),
                                 T.input(type="hidden", name="person", value=who._id),
                                 T.input(type="hidden", name="csrfmiddlewaretoken", value=django.middleware.csrf.get_token(django_request)),
                                 T.button(type="submit", value="request")[button_text]]

def cancel_button(who, eqty_id, role, button_text, django_request):
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST']
    return T.form(action=base+django.urls.reverse("training:cancel"),
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
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST']
    return T.form(action=base+django.urls.reverse("events:signup"),
                  method='POST')[T.input(type="hidden", name="event_id", value=event_id),
                                 T.input(type="hidden", name="person_id", value=who_id),
                                 T.input(type="hidden", name="csrfmiddlewaretoken", value=django.middleware.csrf.get_token(django_request)),
                                 T.button(type="submit", value="cancel_request")[button_text]]

def schedule_event_form(who, extras, button_text, django_request):
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST']
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

def skills_button(area_name, level, which_level):
    return [T.td(class_="level_" + str(which_level))
            [T.input(type='radio',
                     name=area_name,
                     value=str(which_level),
                     checked='checked')
             if level == which_level
             else T.input(type='radio',
                          name=area_name,
                          value=str(which_level))]]

def skills_section(skill_levels, mail_levels, django_request):
    skill_areas = model.configuration.get_config().get('skill_areas', None)
    if skill_areas is None:
        return []
    (mail_1, mail_2, mail_3) = (mail_levels or [False, False, False])
    existing_skills = {area_name: skill_levels.get(area_name, 0) for area_name in skill_areas}
    return [T.form(action="update_levels", method="POST")
            [T.table(class_="skills_check_table")
             [T.thead[T.tr[[T.th["Area"],
                            T.th(class_="level_0")["0"],
                            T.th(class_="level_1")["1"],
                            T.th(class_="level_2")["2"],
                            T.th(class_="level_3")["3"]]]],
              T.tbody[[[T.tr[T.th[area],
                             skills_button(area, existing_skills[area], 0),
                             skills_button(area, existing_skills[area], 1),
                             skills_button(area, existing_skills[area], 2),
                             skills_button(area, existing_skills[area], 3)]]
                       for area in sorted(skill_areas)]],
              T.tfoot[T.tr[T.th["Mail me about events"],
                           T.td[""],
                           T.td[(T.input(type='checkbox', name='mail_1', checked='checked')
                                 if mail_1 else
                                 T.input(type='checkbox', name='mail_1'))],
                           T.td[(T.input(type='checkbox', name='mail_2', checked='checked')
                                 if mail_2 else
                                 T.input(type='checkbox', name='mail_2'))],
                           T.td[(T.input(type='checkbox', name='mail_3', checked='checked')
                                 if mail_3 else
                                 T.input(type='checkbox', name='mail_3'))]]]],
             T.div(align="right")[T.input(type="submit", value="Update interests and skills")]]]

def display_or_form(class_name, action_as_form,
                    headers, row_order,
                    labels_dict, data_dict):
    """Display some data either with or without form inputs to update it."""
    table = T.table(class_=class_name)[
        T.thead[T.tr[[[T.th[header] for header in (headers or ["Key", "Value"])]]]],
        T.tbody[[[T.tr[T.th(class_='ralabel')[labels_dict.get(item, item.capitalize()) if labels_dict else item.capitalize()],
                       T.td[(T.input(type='text',
                                     name='item',
                                     value=data_dict.get(item, ""))
                             if action_as_form
                             else data_dict.get(item, ""))]]]
                                                for item in row_order
                                                if action_as_form or data_dict.get(item, None) != None]],
        T.tfoot[T.tr[T.td[""],
                     T.td[T.input(type='submit',
                                  value=[(labels_dict
                                          or {'submit': "Submit changes"}).get('submit',
                                                                               "Submit changes")])]]]]
    return T.form(action=action_as_form,
                  method='POST')[table] if action_as_form else table

def general_equipment_list(who, viewer, these_types, django_request, detailed=False):
    keyed_types = {eqty.name: eqty for eqty in these_types}
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST']
    return T.table[T.thead[T.tr[T.th["Equipment type"],
                                T.th["Request"],
                                T.th["Admin action"] if viewer.is_administrator() else ""]],
                   T.tbody[[[T.tr[T.th[T.a(href=base
                                           + django.urls.reverse("equiptypes:eqty",
                                                                 args=(name,)))[keyed_types[name].pretty_name()]],
                                  T.td[machinelist(keyed_types[name],
                                                   who, django_request, False) if detailed else "",
                                       toggle_request(who, keyed_types[name]._id, 'user',
                                                      who.has_requested_training([keyed_types[name]._id], 'user'),
                                                      django_request)],
                                  T.td[permit_form(keyed_types[name],
                                                   who._id, who.name(),
                                                   'user',
                                                   django_request)] if viewer.is_administrator() else ""]]
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
                                                              T.input(type="hidden", name="equiptype", value=eqty._id),
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
    if len(raw_reqs) == 0:
        return []
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
            avail_table(model.timeslots.sum_availabilities([person.Person.find(req['requester']).available
                                                      for req in raw_reqs]))]

def special_event_form(eqtype, who_id, role, enable, css_class, button_label, django_request):
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST'] + "/"
    return T.form(action=base+"events/special",
                  class_=css_class,
                  method='POST')[T.input(type='hidden', name='eqtype', value=eqtype._id),
                                 T.input(type='hidden', name='who', value=who_id),
                                 T.input(type='hidden', name='admin_user', value=model.person.Person.find(django_request.user.link_id)._id),
                                 T.input(type='hidden', name='role', value=role),
                                 T.input(type='hidden', name='enable', value=enable),
                                 "Days", T.input(type='text',
                                                 name='duration',
                                                 value="indefinite",
                                                 size=len("indefinite")),
                                 T.input(type="hidden", name="csrfmiddlewaretoken", value=django.middleware.csrf.get_token(django_request)),
                                 T.input(type='submit', value=button_label)]

def permit_form(eqtype, who_id, who_name, role, django_request):
    return special_event_form(eqtype, who_id, role,
                              'True', "permit_form",
                              "Grant " + role + " permission to " + who_name,
                              django_request)

def ban_form(eqtype, who_id, who_name, role, django_request):
    return special_event_form(eqtype, who_id, role,
                              'False', "ban_form",
                              "Ban " + who_name + " as " + role,
                              django_request)

def announcements_section():
    return T.div[T.p["Placeholder."]]
