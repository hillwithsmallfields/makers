from untemplate.throw_out_your_templates_p3 import htmltags as T
import model.configuration
import django.middleware.csrf
import model.equipment_type
import model.event
import pages.page_pieces
import model.pages
import model.person
import model.timeline
import model.timeslots
import datetime

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
    results = [T.table[T.tr[T.th(class_="ralabel")["Title"], T.td[T.a(href=event_link(ev, django_request))[ev.title]]],
                       T.tr[T.th(class_="ralabel")["Event type"], T.td[[ev.event_type]]],
                       T.tr[T.th(class_="ralabel")["Start time"], T.td[model.event.timestring(ev.start)]],
                       T.tr[T.th(class_="ralabel")["End time"], T.td[model.event.timestring(ev.end)]],
                       T.tr[T.th(class_="ralabel")["Location"], T.td[ev.location]],
                       T.tr[T.th(class_="ralabel")["Hosts"], T.td[people_list(ev.hosts)]]]]
    if with_completion:
        completion_table = T.table(class_='event_completion')[T.tr[T.th["Name"],T.th["Unknown"],T.th["No-show"],T.th["Failed"],T.th["Passed"]],
                                                              [T.tr[T.th[all_people_id_to_name[id]],
                                                                    T.tr[result_checkbox(id, "unknown", id not in ev.noshow and id not in ev.failed and id not in ev.passed)],
                                                                    T.tr[result_checkbox(id, "noshow", id in ev.noshow)],
                                                                    T.tr[result_checkbox(id, "failed", id in ev.failed)],
                                                                    T.tr[result_checkbox(id, "passed", id in ev.passed)]]
                                                           for id in ids_in_order]]
        results.append((T.form(action=django.urls.reverse("event:results"),
                              method="POST")[T.input(type="hidden", name='event_id', value=ev._id),
                                             completion_table])
                       if completion_as_form
                       else completion_table)
    return [T.h3[ev.title],
            results]

def event_table_section(tl, django_request, equiptype=None):
    return T.table(class_="timeline_table")[T.tr[T.th["Title"], T.th["Event type"], T.th["Start"], T.th["Location"], T.th["Hosts"], T.th["Equipment"] if equiptype else []],
                                            [T.tr[T.th[ev.title],
                                                  T.td[ev.event_type],
                                                  T.td[model.event.timestring(ev.start)],
                                                  T.td[ev.location],
                                                  T.td[people_list(ev.hosts)],
                                                  T.td[ev.equipment_types] if equiptype else []]
                                             for ev in tl.events()]]
