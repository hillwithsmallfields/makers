from untemplate.throw_out_your_templates_p3 import htmltags as T
from django.http import HttpResponse
import django.urls
import model.equipment_type
import model.event
import model.pages
import model.person
import pages.event_page
import pages.person_page
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def public_index(request):
    """View function for listing the events."""

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)
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

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    params = request.POST # when, submitter, event_type, and anything app-specific: such as: role, equiptype
    print("new_event params are", params)
    machine = params.get('machine', None)
    if machine:
        machine = [machine]
    submitter = model.pages.unstring_id(params['submitter'])
    ev, error_message = model.event.Event.instantiate_template(params['event_type'],
                                                               params['equiptype'],
                                                               [submitter], # todo: override from form
                                                               params['start'],
                                                               machine)
    if ev is None:
        return event_error_page(request, "New event error", error_message)

    print("Made event", ev, "with type", ev.event_type)

    ev.publish()
    ev.invite_available_interested_people()

    page_data = model.pages.HtmlPage("New event confirmation",
                                     pages.page_pieces.top_navigation(request),
                                     django_request=request)

    page_data.add_content("Event details",
                          pages.event_page.one_event_section(ev,
                                                             model.person.Person.find(submitter),
                                                             request))

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def search_events(django_request):
    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    base = request.scheme + "://" + request.META['HTTP_HOST']

    params = request.GET # when, submitter, event_type, and anything app-specific: such as: role, equiptype

    search_params = {}

    # todo: go through the incoming GET params and add any non-blank ones to search_params

    model.timeline.Timeline.creat_timeline(search_params)

    page_data = model.pages.HtmlPage("Event search",
                                     pages.page_pieces.top_navigation(request),
                                     django_request=request)

    page_data.add_content("Events",

                          # todo: probably use pages.event_page.event_table_section

                          pages.event_page.one_event_section(ev,
                                                             model.person.Person.find(submitter),
                                                             request))

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def one_event(django_request, id):
    """View function for looking at one event."""

    print("one_event with id", id, "of type", type(id))

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    ev = model.event.Event.find_by_id(id)

    if ev is None:
        return event_error_page(django_request, "Event display error",
                                "In one_event, could not find event with id " + str(id))

    page_data = model.pages.HtmlPage("Event details",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)

    viewing_user = model.person.Person.find(django_request.user.link_id)
    hosting = True if (viewing_user.is_administrator() or viewing_user._id in ev.hosts) else False

    page_data.add_content("Event details",
                          pages.event_page.one_event_section(ev,
                                                             None, # todo: put person here
                                                             django_request,
                                                             with_completion=hosting, completion_as_form=hosting))

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def signup_event(request):
    """View function for signing up for an event."""

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    params = request.POST # when, submitter, event_type, and anything app-specific: such as: role, equiptype

    event_id = params['event_id']
    print("signup_event with params", params, "and id", event_id, "of type", type(event_id))
    ev = model.event.Event.find_by_id(event_id)

    if ev is None:
        return event_error_page(request, "Event signup page error",
                                "In signup_event, could not find event with id " + str(params['event_id']))

    accepted, rejected = ev.add_signed_up([model.pages.unstring_id(params['person_id'])])

    page_data = model.pages.HtmlPage("Event signup result",
                                     pages.page_pieces.top_navigation(request),
                                     django_request=request)

    page_data.add_content("Event details",
                          pages.event_page.one_event_section(ev,
                                                             None,
                                                             request,
                                                             with_completion=True))

    if accepted == 1:
        page_data.add_content("Result", T.p["%d users added to event, %d not added."%(accepted, rejected)])

    if rejected == 1 and len(ev.signed_up) == ev.attendance_limit:
        page_data.append(T.p["The event was already full."])

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def rsvp_event_form(request, id):
    """View function for choosing whether to sign up for an event from an invitation."""

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    who, what = model.person.Person.mailed_event_details(id)

    if who is None or what is None:
        return event_error_page(request, "Invitation reply error",
                                "In rsvp_event_form, could not find invitation with id " + id)

    page_data = model.pages.HtmlPage("Event invitation reply for " + who.name(),
                                     pages.page_pieces.top_navigation(request),
                                     django_request=request)

    page_data.add_content("Event details",
                          pages.event_page.one_event_section(what,
                                                             who,
                                                             request,
                                                             with_rsvp=True, rsvp_id=id))

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def rsvp_event(django_request):
    """View function for signing up for an event from an invitation."""

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    params = django_request.POST

    id = params['rsvp_id']
    response = params['response']

    who, what = model.person.Person.mailed_event_details(id)

    if who is None or what is None:
        return event_error_page(django_request, "Invitation reply error",
                                "In rsvp_event, could not find invitation with id " + id)

    if response == 'accept':
        what.add_signed_up([who._id])
    elif response == 'decline':
        what.add_invitation_declined([who])
    elif response == 'drop':
        what.add_invitation_declined([who])
        # who.remove_training_request........... # todo: complete this
    else:
        return event_error_page(django_request, "Invitation reply error",
                                "In rsvp_event, a invalid response " + response + " was given for invitation with id " + id)

    page_data = model.pages.HtmlPage("Event reply confirmation",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)

    page_data.add_content("Event details",
                          pages.event_page.one_event_section(what, who, django_request))

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def complete_event(request, id):
    """View function for handling event completion.
    This presents a form for the user (an event host) to fill in."""

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    ev = model.event.Event.find_by_id(id)

    if ev is None:
        return event_error_page(request, "Event completion page error",
                                "In complete_event, could not find event with id " + str(id))

    page_data = model.pages.HtmlPage("Event completion",
                                     pages.page_pieces.top_navigation(request),
                                     django_request=request)

    page_data.add_content("Event details for filling in result",
                          pages.event_page.one_event_section(ev, None,
                                                             request,
                                                             with_completion=True,
                                                             completion_as_form=True))

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def store_event_results(django_request):
    """View function for handling event completion.
    This accepts and confirms the form generated by complete_event."""

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    params = django_request.POST # when, submitter, event_type, and anything app-specific: such as: role, equiptype
    print("in store_event_results with params", params)

    ev = model.event.Event.find_by_id(params['event_id'])

    if ev is None:
        return event_error_page(django_request, "Event recording error",
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

    page_data = model.pages.HtmlPage("Event results recorded",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)

    page_data.add_content("Event details",
                          pages.event_page.one_event_section(ev, None, django_request,
                                                             with_completion=True))

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def special_event(django_request):
    """Create a special event to train or untrain a user.
    This is for administrative override."""
    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

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
