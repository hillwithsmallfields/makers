from django.http import HttpResponse
from untemplate.throw_out_your_templates_p3 import htmltags as T
import pages.page_pieces
import model.configuration
import model.database
import model.equipment_type
import model.pages
import model.person

def list_training(django_request):
    page_data = model.pages.SectionalPage("Training",
                                          pages.page_pieces.top_navigation())
    return HttpResponse(str(page_data.to_string()))

def request_training(django_request):
    page_data = model.pages.SectionalPage("Training request confirmation",
                                          pages.page_pieces.top_navigation())
    params = django_request.POST
    who = model.person.Person.find(params['person'])
    print("looked up", params['person'], "getting", who)
    role = params['role']
    what = model.equipment_type.Equipment_type.find_by_id(params['equiptype'])
    who.add_training_request(role, [what])
    page_data.add_section("Data", [T.p["User " + who.name() + " signed up for " + role + " training on ", what.name + "."]])
    return HttpResponse(str(page_data.to_string()))

def cancel_training_request(django_request):
    page_data = model.pages.SectionalPage("Training request cancellation confirmation",
                                          pages.page_pieces.top_navigation())
    params = django_request.POST
    params = django_request.POST
    who = model.person.Person.find(params['person'])
    role = params['role']
    what = model.equipment_type.Equipment_type.find_by_id(params['equiptype'])
    who.remove_training_request(role, [what])
    page_data.add_section("Data", [T.p["User " + who.name() + " cancelled signup for " + role + " training on ", what.name + "."]])
    return HttpResponse(str(page_data.to_string()))
