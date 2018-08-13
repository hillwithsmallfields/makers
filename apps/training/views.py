from django.http import HttpResponse
from untemplate.throw_out_your_templates_p3 import htmltags as T
import pages.page_pieces
import model.configuration
import model.database
import model.equipment_type
import model.pages
import model.person
from django.views.decorators.csrf import ensure_csrf_cookie

def list_training(django_request):
    page_data = model.pages.SectionalPage("Training",
                                          pages.page_pieces.top_navigation(django_request),
                                          django_request=request)
    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def request_training(django_request):
    page_data = model.pages.HtmlPage("Training request confirmation",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    params = django_request.POST
    model.database.database_init(model.configuration.get_config())
    who = model.person.Person.find(model.pages.unstring_id(params['person']))
    role = params['role']
    what = model.equipment_type.Equipment_type.find_by_id(model.pages.unstring_id(params['equiptype']))
    result, explanation = who.add_training_request(role, what)
    if result:
        page_data.add_content("Data", [T.p["User " + who.name()
                                           + " requested " + role
                                           + " training on ", what.name # todo: linkify this
                                           + "."]])
    else:
        page_data.add_content("Data", [T.p["User " + who.name()
                                           + " could not request " + role
                                           + " training on ", what.name # todo: linkify this
                                           + " because " + explanation
                                           + "."]])
    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def cancel_training_request(django_request):
    page_data = model.pages.SectionalPage("Training request cancellation confirmation",
                                          pages.page_pieces.top_navigation(django_request),
                                          django_request=django_request)
    params = django_request.POST
    model.database.database_init(model.configuration.get_config())
    who = model.person.Person.find(model.pages.unstring_id(params['person']))
    role = params['role']
    what = model.pages.unstring_id(params['equiptype'])
    who.remove_training_request(role, what)
    page_data.add_section("Data", [T.p["User " + who.name() + " cancelled signup for " + role + " training on ", model.equipment_type.Equipment_type.find_by_id(what).name + "."]])
    return HttpResponse(str(page_data.to_string()))
