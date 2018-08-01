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

@ensure_csrf_cookie
def new_event(request):
    """View function for creating an event."""
    params = request.POST # when, submitter, event_type, and anything app-specific: such as: role, equiptype

    ev = model.event.Event.instantiate_template(params['event_type'],
                                          [params['equiptype']],
                                          [params['submitter']],
                                          params['when'])
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

    ev = model.event.Event.find(id)

    page_data = model.pages.HtmlPage("Event details",
                                     pages.page_pieces.top_navigation(request),
                                     django_request=request)

    page_data.add_content("Event details",
                          pages.event_page.one_event_section(ev, request))

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def signup_event(request):
    """View function for signing up for an event."""

    params = django_request.POST # when, submitter, event_type, and anything app-specific: such as: role, equiptype

    ev = model.event.Event.find(params['event_id'])

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

    ev = model.event.Event.find(id)

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

    ev = model.event.Event.find(params['event_id'])

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
def special_event():
    params = django_request.POST
    who = model.person.Person.find(params['who'])
    admin_user = model.person.Person.find(params['admin_user'])
    what = model.equipment_type.Equipment_type.find_by_id(params['what'])
    who.training_individual_event(admin_user, role, what, bool(params['enable']), params['duration'])

    return HttpResponse(pages.person_page.person_page_contents(who, admin_user,
                                                  extra_top_header="Confirmation",
                                                  extra_top_body=T.p[("Permit" if enable else "Ban") + " confirmed"]).to_string)
