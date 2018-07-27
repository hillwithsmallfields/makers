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
        

def one_event_section(ev, django_request, with_completion=False):
    all_people_ids = ev.passed + ev.failed + ev.noshow
    all_people_id_to_name = {p: model.person.Person.find(p).name() for p in all_people_ids}
    all_people_name_and_id = [(all_people_id_to_name[id], id) for id in all_people_id_to_name.keys()]
    ids_in_order = []
    for name in sorted(all_people_id_to_name.values()):
        for pair in all_people_name_and_id:
            if name == pair[0]:
                ids_in_order.append(pair[1])
    results = [T.table[T.tr[T.th(class_="ralabel")["Event type"], T.td[ev.event_type]],
                      T.tr[T.th(class_="ralabel")["Start time"], T.td[ev.timestring(ev.start)]],
                      T.tr[T.th(class_="ralabel")["End time"], T.td[ev.timestring(ev.end)]],
                      T.tr[T.th(class_="ralabel")["Location"], T.td[ev.location]],
                      T.tr[T.th(class_="ralabel")["Hosts"], T.td[people_list(ev.hosts)]],
                      T.tr[T.th(class_="ralabel")["Signed up"], T.td[people_list(ev.signed_up)]],
                      T.tr[T.th(class_="ralabel")["Passed"], T.td[people_list(ev.passed)]],
                      T.tr[T.th(class_="ralabel")["Failed"], T.td[people_list(ev.field)]],
                      T.tr[T.th(class_="ralabel")["Did not attend"], T.td[people_list(ev.noshow)]],
                      T.tr[T.th(class_="ralabel")[""], T.td[ev.]],
                      T.tr[T.th(class_="ralabel")[""], T.td[ev.]]]]
    if with_completion:
        results.append(T.table(class_='event_completion')[T.tr[T.th["Name"],T.th["Unknown"],T.th["No-show"],T.th["Failed"],T.th["Passed"]],
                                                          [T.tr[T.th[all_people_id_to_name[id]],
                                                                T.tr[result_checkbox(id, "unknown", id not in ev.noshow and id not in ev.failed and id not in ev.passed)],
                                                                T.tr[result_checkbox(id, "noshow", id in ev.noshow)],
                                                                T.tr[result_checkbox(id, "failed", id in ev.failed)],
                                                                T.tr[result_checkbox(id, "passed", id in ev.passed)]]
                                                           for id in ids_in_order]])
    return [T.h3[ev.title],
            results]
