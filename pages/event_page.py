from untemplate.throw_out_your_templates_p3 import htmltags as T
import bson
import datetime
import django.middleware.csrf
import model.equipment_type
import model.equipment_type
import model.times
import model.pages
import model.person
import model.timeline
import model.timeslots
import pages.page_pieces

all_conf = None
server_conf = None
org_conf = None

def people_list(pl):
    # todo: perhaps a version with a link for each person (needs per-person privacy controls)
    return ", ".join([model.person.Person.find(p).name() for p in pl if p is not None])

def result_button(id, which, condition):
    return (T.input(type='radio', name=id, value=which, checked='checked')
            if condition
            else T.input(type='radio', name=id, value=which))

def event_link(ev, django_request):
    return django.urls.reverse("events:one_event", args=[ev._id])

def person_name(who):
    descr = model.person.Person.find(who)
    return descr.name() if descr is not None else "<nobody?>"

def avoidances_subsection(ev):
    return T.table(class_='dietary_summary unstriped')[
        [[T.tr[T.td(class_='radata')[str(count)], T.th[what]]]
         for (what, count) in ev.dietary_avoidances_summary()]]

def one_event_section(ev, who, django_request,
                      with_rsvp=False, rsvp_id=None,
                      with_completion=False, completion_as_form=False,
                      allow_editing=False):
    allow_editing = who.is_administrator()
    all_people_ids = ev.signed_up
    all_people_id_to_name = {p: model.person.Person.find(p).name() for p in all_people_ids}
    all_people_name_and_id = [(all_people_id_to_name[id], id) for id in all_people_id_to_name.keys()]
    ids_in_order = []
    for name in sorted(all_people_id_to_name.values()):
        for pair in all_people_name_and_id:
            if name == pair[0]:
                ids_in_order.append(pair[1])
    hosts = people_list(ev.hosts)
    # print("Looking for equipment type", ev.equipment_type)
    eqty = model.equipment_type.Equipment_type.find_by_id(ev.equipment_type)
    eqty_name = eqty.name if eqty else "---"

    results = [(T.table(class_='event_details unstriped')
                [T.tr[T.th(class_='ralabel')["Title"],
                      T.td(class_='event_title')[
                          T.input(type='text', name='title', value=ev.display_title())
                          if allow_editing
                          else T.a(href=event_link(ev, django_request))[ev.display_title()]]],
                 T.tr[T.th(class_='ralabel')["Event type"],
                      T.td(class_='event_type')[
                          T.input(type='text', name='event_type', value=ev.event_type)
                          if allow_editing
                          else ev.event_type]],
                 T.tr[T.th(class_='ralabel')["Start time"],
                      T.td(class_='event_start')[
                          T.input(type='datetime', name='start', value=model.times.timestring(ev.start))
                          if allow_editing
                          else model.times.timestring(ev.start)]],
                 T.tr[T.th(class_='ralabel')["Duration"],
                      T.td(class_='event_duration')[
                          T.input(type='text', name='duration', value=str(ev.end-ev.start))
                          if allow_editing
                          else str(ev.end-ev.start)]],
                 T.tr[T.th(class_='ralabel')["End time"],
                      T.td(class_='event_end')[model.times.timestring(ev.end)]],
                 T.tr[T.th(class_='ralabel')["Location"],
                      T.td(class_='location')[
                          pages.page_pieces.location_dropdown('location', ev.location)
                          if allow_editing
                          else ev.location]],
                 T.tr[T.th(class_='ralabel')["Equipment type"],
                      T.td(class_='event_equipment_type')[
                          pages.page_pieces.equipment_type_dropdown('event_equipment_type', eqty_name)
                          if allow_editing
                          else eqty_name]], # todo: linkify
                 T.tr[T.th(class_='ralabel')["Hosts"],
                      T.td(class_='hosts')[
                          T.input(type='text', name='hosts', value=hosts)
                          if allow_editing
                          else hosts]],
                 T.tr[T.th(class_='ralabel')["Event ID and link"],
                      T.td(class_='event_id')[T.a(href=event_link(ev, django_request))[str(ev._id)]]],
                 (T.tr[T.th(class_='ralabel')[""],
                       T.td[T.input(type='submit', value="Update event details")]]
                  if allow_editing
                  else "")])]

    if ev.catered:
        result += [T.h3["Catering information"],
                   avoidances_subsection(ev)]

    if allow_editing:
        results = [T.form(action=django.urls.reverse("events:update_event"),
                          method='POST')[
                              results,
                              T.input(type='hidden', name='event_id', value=ev._id),
                              T.input(type='hidden',
                                      name='csrfmiddlewaretoken',
                                      value=django.middleware.csrf.get_token(django_request))]]

    if with_rsvp:
        results += [T.h4["Reply to invitation"],
                    T.form(action=django.urls.reverse("events:rsvp"),
                           method='POST')[
                               T.input(type='hidden', name='rsvp_id', value=rsvp_id),
                               T.input(type='hidden', name='csrfmiddlewaretoken', value=django.middleware.csrf.get_token(django_request)),
                               T.ul[T.li[T.input(type='radio', name='response', value='accept'), "Accept"],
                                    T.li[T.input(type='radio', name='response', value='decline'), "Decline"],
                                    T.li[T.input(type='radio', name='response', value='drop'), "Decline and cancel request"]],
                               T.input(type='submit', value="Reply")]]
    if ev.signed_up and len(ev.signed_up) > 0:
        results += [T.h4["Users signed up to event"],
                    T.ul[[[T.li[person_name(sup)]
                           for sup in ev.signed_up]]]]
    # if who._id in ev.signed_up:
    #     pass                    # todo: form to back out of attending event (must rescan to mail waiting list)
    if with_completion:
        completion_table = (T.table(class_='event_completion unstriped')
                            [T.thead[T.tr[T.th["Name"],
                                          T.th(class_='unknown')["Unknown"],
                                          T.th(class_='no_show')["No-show"],
                                          T.th(class_='failed')["Failed"],
                                          T.th(class_='passed')["Passed"]]],
                             T.tbody[[[T.tr[T.th[all_people_id_to_name[id]],
                                            (T.td(class_='unknown')
                                             [result_button(id,
                                                            "unknown",
                                                            (id not in ev.noshow
                                                             and id not in ev.failed
                                                             and id not in ev.passed))]),
                                            (T.td(class_='no_show')
                                             [result_button(id,
                                                            "noshow",
                                                            id in ev.noshow)]),
                                            (T.td(class_='failed')
                                             [result_button(id,
                                                            "failed",
                                                            id in ev.failed)]),
                                            (T.td(class_='passed')
                                             [result_button(id,
                                                            "passed",
                                                            id in ev.passed)])]
                                       for id in ids_in_order]]],
                             (T.tfoot[T.tr[T.td(colspan="2")[""],
                                          T.td(colspan="3")[T.input(type='submit',
                                                                    value="Record results")]]]
                              if completion_as_form
                              else "")])
        # todo: signup if in the future
        results += [T.h4["Results"],
                    ((T.form(action=django.urls.reverse("events:results"),
                             method="POST")[T.input(type='hidden',
                                                    name='event_id',
                                                    value=ev._id),
                                            T.input(type='hidden',
                                                    name='csrfmiddlewaretoken',
                                                    value=django.middleware.csrf.get_token(django_request)),
                                            completion_table])
                     if completion_as_form
                     else completion_table)]
    return [T.h3[ev.title.replace('_', ' ').capitalize() if ev.title else "Event"],
            results]

def equip_name(eqid):
    eqt = model.equipment_type.Equipment_type.find_by_id(eqid)
    if eqt:
        return eqt.pretty_name()
    else:
        return "unknown"

def event_table_section(tl_or_events, who_id, django_request,
                        show_equiptype=False,
                        with_signup=False,
                        with_completion_link=False,
                        allow_editing=False):
    events = tl_or_events.events() if isinstance(tl_or_events, model.timeline.Timeline) else tl_or_events
    now = model.times.now()
    return (T.table(class_='timeline_table unstriped')
            [T.thead[T.tr[T.th["Title"], T.th["Event type"], T.th["Start"], T.th["Location"], T.th["Hosts"],
                          T.th["Equipment"] if show_equiptype else "",
                          T.th["Sign up"] if with_signup else "",
                          T.th["Record results"] if with_completion_link else ""]],
             T.tbody[[[T.tr[T.th(class_='event name')[T.a(href=event_link(ev, django_request))[ev.display_title()]],
                            T.td(class_='event')[ev.event_type],
                            T.td(class_='event datetime')[model.times.timestring(ev.start)],
                            T.td(class_='event location')[ev.location],
                            T.td(class_='event humanid emph hosts')[people_list(ev.hosts)],
                            (T.td(class_='event eqtys')[equip_name(ev.equipment_type)]
                             if show_equiptype
                             else ""),
                            (T.td[pages.page_pieces.signup_button(ev._id, who_id, "Sign up", django_request)]
                             if with_signup and model.times.as_utc(ev.start) > now
                             else ""),
                            (T.td[T.a(href=django.urls.reverse("events:done_event", args=(ev._id,)))["Record results"]]
                             if with_completion_link and model.times.as_utc(ev.start) < now
                             else "")]]
                      for ev in events]]])
