from django.http import HttpResponse
import pages.event_page
import model.pages

# Create your views here.

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

def new_event(request):
    """View function for creating an event."""
    params = django_request.POST # when, submitter, event_type, and anything app-specific: such as: role, equiptype

    ev = event.Event.instantiate_template(params['event_type'],
                                          [params['equiptype']],
                                          [params['submitter']],
                                          params['when'])
    ev.publish()

    page_data = model.pages.HtmlPage("New event confirmation",
                                     pages.page_pieces.top_navigation(request))

    page_data.add_content("Event details",
                          pages.event_page.one_event_section(ev, request))

    return HttpResponse(str(page_data.to_string()))

def one_event(request, id):
    """View function for looking at one event."""

    ev = event.Event.find(id)
    
    page_data = model.pages.HtmlPage("Event details",
                                     pages.page_pieces.top_navigation(request))

    page_data.add_content("Event details",
                          pages.event_page.one_event_section(ev, request))

    return HttpResponse(str(page_data.to_string()))

def complete_event(request, id):
    """View function for handling event completion."""

    ev = event.Event.find(id)
    
    page_data = model.pages.HtmlPage("Event completion",
                                     pages.page_pieces.top_navigation(request))

    page_data.add_content("Event details",
                          pages.event_page.one_event_section(ev, request,
                                                             with_completion=True,
                                                             completion_as_form=True))

    return HttpResponse(str(page_data.to_string()))

def store_event_results(request):
    """View function for handling event completion."""

    params = django_request.POST # when, submitter, event_type, and anything app-specific: such as: role, equiptype

    ev = event.Event.find(params['event_id'])

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
                                     pages.page_pieces.top_navigation(request))

    page_data.add_content("Event details",
                          pages.event_page.one_event_section(ev, request,
                                                             with_completion=True))

    return HttpResponse(str(page_data.to_string()))
