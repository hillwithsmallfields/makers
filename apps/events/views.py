from untemplate.throw_out_your_templates_p3 import htmltags as T
from django.http import HttpResponse
import model.equipment_type
import model.event
import model.pages
import model.person
import pages.event_page
import pages.person_page
from django.views.decorators.csrf import ensure_csrf_cookie

# Create your views here.

@ensure_csrf_cookie
def public_index(request):
    """View function for listing the events."""
    return HttpResponse("""
    <html>
    <head><title>Events list placeholder</title></head>
    <body><h1>Events list placeholder</h1>
    <p>This is where the list of events will go.</p>
    </body>
    </html>
    """)

def event_error_page(request, label, error_message):
    page_data = model.pages.HtmlPage(label,
                                     pages.page_pieces.top_navigation(request),
                                     django_request=request)

    page_data.add_content("Event details",
                          T.p[error_message])

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def new_event(request):
    """View function for creating an event."""
    params = request.POST # when, submitter, event_type, and anything app-specific: such as: role, equiptype
    print("new_event params are", params)
    machine = params.get('machine', None)
    if machine:
        machine = [machine]
    ev, error_message = model.event.Event.instantiate_template(params['event_type'],
                                                               params['equiptype'],
                                                               [params['submitter']],
                                                               params['when'],
                                                               machine)
    if ev is None:
        return event_error_page(request, "New event error", error_message)

    ev.publish()
    ev.invite_available_interested_people()

    page_data = model.pages.HtmlPage("New event confirmation",
                                     pages.page_pieces.top_navigation(request),
                                     django_request=request)

    page_data.add_content("Event details",
                          pages.event_page.one_event_section(ev, request))

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def one_event(request, id):
    """View function for looking at one event."""

    print("one_event with id", id, "of type", type(id))

    ev = model.event.Event.find_by_id(model.pages.unstring_id(id))

    if ev is None:
        return event_error_page(request, "Event display error",
                                "In one_event, could not find event with id " + str(id))

    page_data = model.pages.HtmlPage("Event details",
                                     pages.page_pieces.top_navigation(request),
                                     django_request=request)

    page_data.add_content("Event details",
                          pages.event_page.one_event_section(ev, request))

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def signup_event(request):
    """View function for signing up for an event."""

    params = request.POST # when, submitter, event_type, and anything app-specific: such as: role, equiptype
    print("in signup_event with params", params)

    ev = model.event.Event.find_by_id(model.pages.unstring_id(params['event_id']))

    if ev is None:
        return event_error_page(request, "Event signup page error",
                                "In signup_event, could not find event with id " + str(params['event_id']))

    ev.invitation_accepted.append(params['person_id'])

    page_data = model.pages.HtmlPage("Event completion",
                                     pages.page_pieces.top_navigation(request),
                                     django_request=request)

    page_data.add_content("Event details",
                          pages.event_page.one_event_section(ev, request,
                                                             with_completion=True))

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def complete_event(request, id):
    """View function for handling event completion."""

    ev = model.event.Event.find_by_id(model.pages.unstring_id(id))

    if ev is None:
        return event_error_page(request, "Event completion page error",
                                "In complete_event, could not find event with id " + str(id))

    page_data = model.pages.HtmlPage("Event completion",
                                     pages.page_pieces.top_navigation(request),
                                     django_request=request)

    page_data.add_content("Event details",
                          pages.event_page.one_event_section(ev, request,
                                                             with_completion=True,
                                                             completion_as_form=True))

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def store_event_results(request):
    """View function for handling event completion."""

    params = django_request.POST # when, submitter, event_type, and anything app-specific: such as: role, equiptype
    print("in store_event_results with params", params)

    ev = model.event.Event.find_by_id(model.pages.unstring_id(params['event_id']))

    if ev is None:
        return event_error_page(request, "Event recording error",
                                "In store_event_results, could not find event with id " + str(params['event_id']))

    noshow = []
    failed = []
    passed = []
    for person_id, value in params.items():
        if person_id == 'event_id':
            continue
        if value == 'noshow':
            noshow.append(person_id)
        if value == 'failed':
            failed.append(person_id)
        if value == 'passed':
            passed.append(person_id)
    ev.mark_results(passed, failed, noshow)

    page_data = model.pages.HtmlPage("Event completion",
                                     pages.page_pieces.top_navigation(request),
                                     django_request=request)

    page_data.add_content("Event details",
                          pages.event_page.one_event_section(ev, request,
                                                             with_completion=True))

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def special_event(django_request):
    params = django_request.POST
    print("in special_event with params", params)
    who = model.person.Person.find(model.pages.unstring_id(params['who']))
    admin_user = model.person.Person.find(model.pages.unstring_id(params['admin_user']))
    what = model.equipment_type.Equipment_type.find_by_id(params['eqtype'])
    enable = params['enable'] == 'True'
    who.training_individual_event(admin_user,
                                  params['role'],
                                  what,
                                  enable,
                                  None,
                                  params['duration'])

    return HttpResponse(str(pages.person_page.person_page_contents(who, admin_user, django_request,
                                                                   extra_top_header="Confirmation",
                                                                   extra_top_body=T.p[("Permit"
                                                                                       if enable
                                                                                       else "Ban")
                                                                                      + " confirmed"]).to_string()))
