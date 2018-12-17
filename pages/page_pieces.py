from untemplate.throw_out_your_templates_p3 import htmltags as T
import django.urls
import model.configuration
import model.database
import model.equipment_type
import model.event
import model.machine
import model.person
import model.timeline
import model.times
import model.timeslots
import datetime

"""Assorted useful bits of expressions for constructing our pages."""

server_conf = None

def set_server_conf():
    global server_conf
    server_conf = model.configuration.get_config('server')

def top_navigation(django_request):
    org_conf = model.configuration.get_config('organization')
    # todo: make this a bar of buttons, or a dropdown
    return [T.nav(class_='top_nav')
            [T.ul[T.li[T.a(href=org_conf['home_page'])["[" + org_conf['title'] + " home]"]],
                  T.li[T.a(href=org_conf['wiki'])["[Wiki]"]],
                  T.li[T.a(href=org_conf['forum'])["[Forum]"]],
                  T.li[T.a(href=django.urls.reverse("dashboard:own_dashboard"))["[Your dashboard]"]],
                  T.li[T.a(href='/users/logout')["[Logout]"]]]]]     # todo: use reverse when I can find its name

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
                  method='POST')[T.input(type='hidden', name='equiptype', value=eqty_id),
                                 T.input(type='hidden', name='role', value=role),
                                 T.input(type='hidden', name='person', value=who._id),
                                 T.input(type='hidden', name='csrfmiddlewaretoken', value=django.middleware.csrf.get_token(django_request)),
                                 T.button(type='submit', value="request")[button_text]]

def cancel_button(who, eqty_id, role, button_text, django_request):
    return T.form(action=django.urls.reverse("training:cancel"),
                  method='POST')[T.input(type='hidden', name='equiptype', value=eqty_id),
                                 T.input(type='hidden', name='role', value=role),
                                 T.input(type='hidden', name='person', value=who._id),
                                 T.input(type='hidden', name='csrfmiddlewaretoken', value=django.middleware.csrf.get_token(django_request)),
                                 T.button(type='submit', value="cancel_request")[button_text]]

def toggle_request(who, eqty, role, already_requested, django_request):
    return (request_button(who, eqty, role, "Request %s training"%role, django_request)
            if not already_requested
            else cancel_button(who, eqty, role, "Cancel %s training request"%role, django_request))

def signup_button(event_id, who_id, button_text, django_request):
    return T.form(action=django.urls.reverse("events:signup"),
                  method='POST')[T.input(type='hidden', name='event_id', value=event_id),
                                 T.input(type='hidden', name='person_id', value=who_id),
                                 T.input(type='hidden', name='csrfmiddlewaretoken', value=django.middleware.csrf.get_token(django_request)),
                                 T.button(type='submit', value="cancel_request")[button_text]]

def schedule_event_form(who, extras, button_text, django_request):
    return (T.form(action=django.urls.reverse("events:new_event"),
                   method='POST')
            ["Date and time: ", T.input(type='datetime', name='when'), T.br,
             extras,
             T.input(type='hidden', name='submitter', value=str(who._id)),
             T.input(type='hidden', name='csrfmiddlewaretoken', value=django.middleware.csrf.get_token(django_request)),
             T.button(type='submit', class_='button_schedule_event', value="schedule")[button_text]])

def availform(who, available, django_request):
    days, _, times = model.timeslots.get_slots_conf()
    return (T.div(class_='weekly_slots availability')
            [T.form(action=django.urls.reverse("dashboard:update_availability"),
                    method="POST")
             [T.table(class_='availability unstriped')
              [[T.thead[T.tr[T.th(class_='daylabel')["Day"],
                             [[T.th[slotname]] for slotname in times]]]],
               T.tbody[[[T.tr[T.th(class_='daylabel')[day],
                              [T.td[T.input(type='checkbox',
                                            name=day+"_"+t, checked="checked")
                                    if b
                                    else T.input(type='checkbox',
                                                 name=day+"_"+t)]
                               for t, b in zip(times, day_slots)]]]
                        for (day, day_slots) in zip(days,
                                                    model.timeslots.timeslots_from_int(available))]]],
              T.input(type='hidden', name='csrfmiddlewaretoken', value=django.middleware.csrf.get_token(django_request)),
              T.input(type='hidden', name='person', value=str(who._id)),
              T.input(type='submit', class_='button_update', value="Update availability")]])

def avail_table(who, slot_sums):
    days, _, times = model.timeslots.get_slots_conf()
    return [T.div(class_='weekly_slots avail_table')[
        [T.h4["Availability of people who have requested training"],
         T.table(class_='availability unstriped')
         [T.thead[T.tr[T.th(class_='daylabel')["Day"],
                       [[T.th[slotname]] for slotname in times]]],
          T.tbody[[[T.tr[T.th(class_='daylabel')[day],
                         [T.td[str(b) # todo: make bold, and a different style, if "who" (the viewing user) is available then
                           ]
                          for t, b in zip(times, day_slots)]]]
                   for (day, day_slots) in zip(days,
                                               model.timeslots.avsums_by_day(slot_sums))]]]]]]

def schedule_training_event_form(who, role, eqtype, extras, button_text, django_request):
    event_type = role+"_training"
    people_awaiting_training = [who for who in model.person.Person.awaiting_training(event_type, eqtype._id)]
    return [
        avail_table(who,
                    model.timeslots.sum_availabilities([
            who.available
            for who in people_awaiting_training])) if len(people_awaiting_training) > 0 else "",
        T.br,
        schedule_event_form(who, [T.input(type='hidden', name='event_type', value=event_type),
                                  T.input(type='hidden', name='role', value=role),
                                  T.input(type='hidden', name='equiptype', value=eqtype._id)] + extras,
                            button_text, django_request)]

def interests_button(area_name, level, which_level):
    return [T.td(class_='level_' + str(which_level))
            [T.input(type='radio',
                     name=area_name,
                     value=str(which_level),
                     checked='checked')
             if level == which_level
             else T.input(type='radio',
                          name=area_name,
                          value=str(which_level))]]

def interests_section(interest_levels, mail_levels, django_request, for_person=None):
    interest_areas = model.configuration.get_config('interest_areas')
    if interest_areas is None:
        return []
    existing_interests = {area_name: interest_levels.get(area_name, 0) for area_name in interest_areas}
    return [T.form(action=django.urls.reverse("dashboard:update_levels"), method="POST")
            [T.table(class_='interests_check_table unstriped')
             [T.thead[T.tr[[T.th["Area"],
                            [[[T.th(class_='level_'+str(lev))[str(lev)]] for lev in range(4)]]]]],
              T.tbody[[[T.tr[T.th[area],
                             [[[interests_button(area, existing_interests[area], lev)] for lev in range(4)]]]]
                       for area in sorted(interest_areas)]],
              (T.tfoot[T.tr[T.th["Mail me about events"],
                            T.td[""],
                            [[[T.td[(T.input(type='checkbox', name='mail_'+str(lev), checked='checked')
                                     if mail_levels[lev]
                                     else T.input(type='checkbox', name='mail_'+str(lev)))]] for lev in range(1,4)]]]] if mail_levels else "")],
             T.input(type='hidden', name='csrfmiddlewaretoken', value=django.middleware.csrf.get_token(django_request)),
             # This form can be used either for a person, or for an event
             T.input(type='hidden', name='subject_user_uuid', value=for_person._id) if for_person else "",
             T.div(align='right')[T.input(type='submit', class_='button_update', value="Update interests")]],
            T.input(type='hidden', name='csrfmiddlewaretoken', value=django.middleware.csrf.get_token(django_request))]

def plain_value(item):
    return item[0] if type(item) == tuple else item

def linked_value(item):
    return T.href(a=item[1])[item[0]] if type(item) == tuple else item

def display_or_form(class_name, action_as_form,
                    headers, row_order,
                    labels_dict, data_dict):
    """Display some data either with or without form inputs to update it."""
    table = T.table(class_=class_name+ ' unstriped')[
        T.thead[T.tr[[[T.th[header] for header in (headers or ["Key", "Value"])]]]],
        T.tbody[[[T.tr[T.th(class_='ralabel')[(labels_dict.get(item, item.capitalize())
                                               if labels_dict
                                               else item.capitalize())],
                       T.td[(T.input(type='text',
                                     name='item',
                                     value=plain_value(data_dict.get(item, "")))
                             if action_as_form
                             else linked_value(data_dict.get(item, "")))]]]
                 for item in row_order
                 if (action_as_form # display all the fields, even blank ones, if presenting a form
                     # if presenting a read-only display, skip any blank fields:
                     or data_dict.get(item, None) != None)]],
        T.tfoot[T.tr[T.td[""],
                     T.td[T.input(type='submit',
                                  value=[(labels_dict
                                          or {'submit': "Submit changes"}).get('submit',
                                                                               "Submit changes")])]]]]
    return T.form(action=action_as_form,
                  method='POST')[table] if action_as_form else table

def general_equipment_list(who, viewer, these_types, django_request, detailed=False):
    keyed_types = {eqty.name: eqty for eqty in these_types}
    return T.table(class_='equipment_type_list unstriped')[
        T.thead[T.tr[T.th["Equipment type"],
                     T.th["Request"],
                     T.th["Admin action"] if viewer.is_administrator() else ""]],
        T.tbody[[[T.tr[T.th(class_='category_'+keyed_types[name].training_category)[
            T.a(href=django.urls.reverse("equiptypes:eqty",
                                         args=(name,)))[keyed_types[name].pretty_name()]],
                       T.td[machinelist(keyed_types[name],
                                        who, django_request, False) if detailed else "",
                            (toggle_request(who, keyed_types[name]._id, 'user',
                                            who.has_requested_training(keyed_types[name]._id, 'user'),
                                            django_request)
                                        if keyed_types[name].training_category != "green"
                                        else "Training not required")],
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
    # todo: make this into an accordion
    return ([T.table(class_='machine_list unstriped')[
        T.thead[T.tr[T.th["Machine"], T.th["Status"], T.th["Owner actions" if as_owner else ""]]],
        T.tbody[[[T.tr[T.th[machine_link(device.name)],
                       T.td[device.status],
                       T.td[schedule_event_form(who,
                                                [T.input(type='hidden', name='machine', value=device.name),
                                                 T.input(type='hidden', name='equiptype', value=eqty._id),
                                                 T.input(type='hidden', name='event_type', value="maintenance")],
                                                "Schedule maintenance",
                                                django_request)
                                 if as_owner else ""]]]
                              for device in mclist]]]]
            if mclist
            else [])

def eqty_training_requests(eqtype, django_request):
    raw_reqs = eqtype.get_training_requests()
    # print("raw_reqs is", raw_reqs)
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
    # print("reqs are", reqs)
    return [T.table(class_='unstriped')[
        T.thead[T.tr[T.th["Date requested"],
                     T.th["Requester"]]],
        T.tbody[[[T.tr[T.td[event.timestring(req['request_date'])],
                       T.td[person.Person.find(req['requester']).name()]]]
                            for req in reqs]]],
            avail_table(model.person.Person.find(django_request.user.link_id),
                        model.timeslots.sum_availabilities([person.Person.find(req['requester']).available
                                                      for req in raw_reqs]))]

def special_event_form(eqtype, who_id, role, enable, css_class, button_label, django_request):
    return T.form(action=django.urls.reverse("events:special"),
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
                                 T.input(type='hidden', name='csrfmiddlewaretoken', value=django.middleware.csrf.get_token(django_request)),
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
    announcements = model.database.get_announcements(None, 3)
    return T.div[T.dl[[[T.dt[model.times.timestring(a['when'])],
                        T.dd[a['text']]] for a in announcements]]]

def dropdown(name, choices, current=None):
    """Make an HTML form dropdown box."""
    return T.select(name=name)[[(T.option(value=item,
                                          selected='selected')[choices[item]]
                                 if item==current
                                 else T.option(value=item)[choices[item]])
                                for item in sorted(choices.keys())]
                               if type(choices) == dict
                               else [(T.option(value=item,
                                               selected='selected')[item]
                                      if item==current
                                      else T.option(value=item)[item])
                                     for item in choices]]

def equipment_type_dropdown(name, current=None):
    """Return a chooser for equipment types."""
    eq_types = {etype.name: etype.pretty_name()
                for etype in model.equipment_type.Equipment_type.list_equipment_types()}
    eq_types.update({'---': None})
    return dropdown(name,
                    {eqty: eqty.replace('_', ' ').capitalize() for eqty in eq_types},
                    # current.replace('_', ' ').capitalize() if current else '---'
                    current if current else '---'
    )

def event_template_dropdown(name, current=None):
    templates = {template['name']: template['event_type']
                 for template in model.event.Event.list_templates([], None)}
    templates.update({'---': None}),
    return dropdown(name,
                    templates,
                    current or '---')

def location_dropdown(name, current=None):
    return dropdown(name,
                    sorted(model.configuration.get_location_names() + ['---']),
                    current or '---')
