from untemplate.throw_out_your_templates_p3 import htmltags as T
import datetime
import django.middleware.csrf
import model.configuration
import model.equipment_type
import model.equipment_type
import model.event
import model.pages
import model.person
import model.timeline
import model.timeslots
import pages.page_pieces

all_conf = None
server_conf = None
org_conf = None

def people_list(pl):
    return ", ".join(model.person.Person.find(p).name() for p in pl)

def checkbox(id, which, condition):
    return (T.input(name=id, value=which, checked='checked')
            if condition
            else T.input(name=id, value=which))

def event_link(ev, django_request):
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST'] + "/"
    return base + django.urls.reverse("events:oneevent") + "/" + ev._id

def one_event_section(ev, django_request, with_completion=False, completion_as_form=False):
    all_people_ids = ev.passed + ev.failed + ev.noshow
    all_people_id_to_name = {p: model.person.Person.find(p).name() for p in all_people_ids}
    all_people_name_and_id = [(all_people_id_to_name[id], id) for id in all_people_id_to_name.keys()]
    ids_in_order = []
    for name in sorted(all_people_id_to_name.values()):
        for pair in all_people_name_and_id:
            if name == pair[0]:
                ids_in_order.append(pair[1])
    results = [(T.table(class_='event_details')
                [T.tr[T.th(class_="ralabel")["Title"], T.td(class_="event_title")[T.a(href=event_link(ev, django_request))[ev.title]]],
                 T.tr[T.th(class_="ralabel")["Event type"], T.td(class_="event_type")[ev.event_type]],
                 T.tr[T.th(class_="ralabel")["Start time"], T.td(class_="event_start")[model.event.timestring(ev.start)]],
                 T.tr[T.th(class_="ralabel")["End time"], T.td(class_="event_end")[model.event.timestring(ev.end)]],
                 T.tr[T.th(class_="ralabel")["Location"], T.td(class_="location")[ev.location]],
                 T.tr[T.th(class_="ralabel")["Equipment types"], T.td(class_="event_equipment_types")[", ".join([model.equipment_type.Equipment_type.find_by_id(x).name for x in ev.equipment_types])]],
                 T.tr[T.th(class_="ralabel")["Hosts"], T.td(class_="hosts")[people_list(ev.hosts)]]])]
    if with_completion:
        completion_table = T.table(class_='event_completion')[T.tr[T.th["Name"],T.th["Unknown"],T.th["No-show"],T.th["Failed"],T.th["Passed"]],
                                                              [T.tr[T.th[all_people_id_to_name[id]],
                                                                    T.td[result_checkbox(id, "unknown", id not in ev.noshow and id not in ev.failed and id not in ev.passed)],
                                                                    T.td[result_checkbox(id, "noshow", id in ev.noshow)],
                                                                    T.td[result_checkbox(id, "failed", id in ev.failed)],
                                                                    T.td[result_checkbox(id, "passed", id in ev.passed)]]
                                                           for id in ids_in_order]]
        results.append((T.form(action=django.urls.reverse("event:results"),
                              method="POST")[T.input(type="hidden", name='event_id', value=ev._id),
                                             completion_table])
                       if completion_as_form
                       else completion_table)
        # todo: signup if in the future
    return [T.h3[ev.title],
            results]

def event_table_section(tl, who_id, django_request, equiptype=None, with_signup=False):
    return (T.table(class_="timeline_table")
            [T.thead[T.tr[T.th["Title"], T.th["Event type"], T.th["Start"], T.th["Location"], T.th["Hosts"],
                          T.th["Equipment"] if equiptype else "",
                          T.th["Sign up"] if with_signup else ""]],
             T.tbody[[[T.tr[T.th(class_="event_title")[ev.title],
                            T.td(class_="event_type")[ev.event_type],
                            T.td(class_="event_start")[model.event.timestring(ev.start)],
                            T.td(class_="location")[ev.location],
                            T.td(class_="hosts")[people_list(ev.hosts)],
                            T.td(class_="event_equipment_type")[ev.equipment_type] if equiptype else [],
                            T.td[signup_button(ev._id, who_id, "Sign up")] if with_signup else ""]]
                      for ev in tl.events()]]])
