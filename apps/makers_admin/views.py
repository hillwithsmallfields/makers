from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from untemplate.throw_out_your_templates_p3 import htmltags as T
import django.urls
import model.configuration
import model.database           # for announcements and notifications; I should probably wrap them so apps don't need to see model.database
import model.django_calls
import model.equipment_type
import model.event
import model.makers_server
import model.pages
import model.person
import pages.event_page
import pages.person_page

# from https://stackoverflow.com/questions/17873855/manager-isnt-available-user-has-been-swapped-for-pet-person,
# replacing: from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()

def admin_error_page(request, label, error_message):
    page_data = model.pages.HtmlPage(label,
                                     pages.page_pieces.top_navigation(request),
                                     django_request=request)

    page_data.add_content("Details",
                          T.p[error_message])

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def create_event(django_request):

    """The first stage of event creation.
    This sets up the parameters based on the event template."""

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    viewer = model.person.Person.find(django_request.user.link_id)

    request_params = django_request.GET

    template_name = request_params.get('event_type', None)
    if template_name is None or template_name == "":
        return admin_error_page(django_request, "Event creation error",
                                "No template name given")

    equipment_type = request_params.get('equipment_type', "")
    suggested_time = request_params.get('start', "")

    template = model.event.Event.find_template(template_name)

    page_data = model.pages.HtmlPage("Create event",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)

    form = T.form(action=django.urls.reverse("makers_admin:create_event_2"),
                  method='POST')[T.input(type="hidden",
                                         name="csrfmiddlewaretoken",
                                         value=django.middleware.csrf.get_token(django_request)),
                                 T.table[T.tr[T.th(class_="ralabel")["When"],
                                              T.td[T.input(type='datetime',
                                                           name='start',
                                                           value=suggested_time)]],
                                         T.tr[T.th(class_="ralabel")["Equipment type"],
                                              T.td[pages.page_pieces.equipment_type_dropdown('equipment_type',
                                                                                             equipment_type)]],
                                         [[T.tr[T.th(class_="ralabel")[k.replace('_', ' ').capitalize()],
                                                T.td[T.input(type='text',
                                                             name=k,
                                                             value=str(template[k]).replace('$equipment',
                                                                                            equipment_type))]]]
                                          for k in sorted(template.keys())
                                          if k != '_id'],
                                         T.tr[T.td[""], T.td[T.input(type='submit', value="Create event")]]]]

    page_data.add_content("Event creation form", model.pages.with_help(viewer, form, "event_creation"))
    return HttpResponse(str(page_data.to_string()))

def as_boolean(x):
    return x in [True, 'True', 'Yes', 'yes', 'On', 'on']

values_requiring_splitting = None
values_as_integers = None
values_as_booleans = None
values_as_times = None

def process_value(k, v):
    return ([v.strip() for v in v.split(',')]
            if k in values_requiring_splitting
            else (int(v)
                  if k in values_as_integers
                  else (model.times.as_time(v)
                        if k in values_as_times
                        else (as_boolean(v)
                              if k in values_as_booleans
                              else v))))

def host_list(host_string, user):
    if host_string is None or host_string == "":
        return [model.person.Person.find(user)._id]
    return [model.person.Person.find(host)._id for host in host_string.split(',')]

def create_event_2(django_request):

    """The second stage of event creation."""

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    global values_requiring_splitting, values_as_integers, values_as_times
    if values_requiring_splitting is None:
        values_requiring_splitting = config_data['event_templates']['needing_splitting']
    if values_as_integers is None:
        values_as_integers = config_data['event_templates']['as_integers']
    if values_as_booleans is None:
        values_as_booleans = config_data['event_templates']['as_booleans']
    if values_as_times is None:
        values_as_times = config_data['event_templates']['as_times']
    params = django_request.POST

    ev = model.event.Event(params.get('event_type', 'Meeting'),
                           model.times.as_time(params.get('start')),
                           host_list(params.get('hosts', None),
                                 django_request.user.link_id))

    ev.__dict__.update({k:process_value(k, v) for k, v in params.items()})

    ev.save()

    page_data = model.pages.HtmlPage(
        "Event created",
        pages.page_pieces.top_navigation(django_request),
        django_request=django_request)

    page_data.add_content(
        "Event creation confirmation",
        pages.event_page.one_event_section(
            ev,
            model.person.Person.find(django_request.user.link_id),
            django_request))

    return HttpResponse(str(page_data.to_string()))

def announce(django_request):

    """Send an announcement to everyone."""

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    text = django_request.POST['announcement']

    when = datetime.utcnow()

    model.database.add_announcement(when,
                                    model.person.Person.find(django_request.user.link_id)._id,
                                    text)

    page_data = model.pages.HtmlPage("Announce",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content("Announcement confirmation", text)
    return HttpResponse(str(page_data.to_string()))

def notify(django_request):

    """Send a notification to someone."""

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    text = django_request.POST['message']
    to = django_request.POST['to']

    model.database.add_notification(to,
                                    datetime.utcnow(),
                                    text)

    page_data = model.pages.HtmlPage("Notify",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content("Confirmation of notification to " + model.person.Person.find(to).name(), text)
    return HttpResponse(str(page_data.to_string()))

def send_email(django_request):

    """Send an email to someone."""

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    text = django_request.POST['message']
    subject = django_request.POST['subject']
    to = django_request.POST['to']

    model.makers_server.mailer(to, subject, text)

    page_data = model.pages.HtmlPage("send_email",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content("Confirmation of email to " + to + " about " + subject, text)
    return HttpResponse(str(page_data.to_string()))

def make_login(given_name, surname):
    login_base = ((given_name[:3] if len(given_name) > 3 else given_name)
                  + (surname[:3] if len(surname) > 3 else surname))
    # todo: look for the lowest number that is unused so far for this login_base
    return login_base + "1"

def create_django_user(login_name, email, given_name, surname, link_id):
    # based on https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Authentication
    # Create user and save to the database
    print("create_django_user creating django_user")
    django_user = User.objects.create_user(login_name, email, '')

    # Update fields and then save again
    django_user.first_name = given_name
    django_user.last_name = surname
    django_user.link_id = link_id
    print("create_django_user setting unusable password")
    django_user.set_unusable_password()
    print("create_django_user saving data")
    django_user.save()
    print("create_django_user sending email")
    model.django_calls.send_password_reset_email(model.person.Person.find(link_id))
    print("create_django_user complete")

@ensure_csrf_cookie
def add_user(django_request):

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    params = django_request.POST
    # print("add_user params are", {k:v for k, v in params.items()})
    given_name = params['given_name']
    surname = params['surname']
    email = params['email']
    login = make_login(given_name, surname)
    induction_event = None

    link_id = model.database.add_person({'email': email,
                                         'given_name': given_name,
                                         'surname': surname,
                                         'known_as': given_name},
                                        {'login_name': login})
    create_django_user(login, email, given_name, surname, link_id)

    if params['inducted']:
        induction_id = params.get('induction_event', None)
        induction_event = model.event.Event.find_by_id(model.pages.unstring_id(induction_id)) if induction_id else None
        # print("Marking new user as inducted, induction_id is", induction_id, "and induction_event is", induction_event)
        if induction_event is None:
            facility_name = model.configuration.get_config('organization', 'name')
            eqty = model.equipment_type.Equipment_type.find(facility_name)
            induction_event = model.event.Event("user_training",
                                                model.times.now(),
                                                [model.person.Person.find(django_request.user.link_id)._id],
                                                equipment_type=eqty._id,
                                                event_duration=0)
            # print("Made new induction event", induction_event, "for facility named", facility_name, "which is equipment type", eqty)
        induction_event.mark_results([model.person.Person.find(link_id)], [], [])
        # print("induction event has _id", induction_event._id)

    page_data = model.pages.HtmlPage("Added user",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content("Confirmation of adding user " + given_name + " " + surname,
                          [T.h2["Add another user"],
                           pages.person_page.add_user_form(django_request,
                                                           induction_event._id)])
    return HttpResponse(str(page_data.to_string()))

def template_field(name, value):
    return (value
            if name == '_id'
            else (pages.page_pieces.equipment_type_dropdown('equipment_type', value)
                  if name == 'equipment_type'
                  else (pages.page_pieces.location_dropdown('location', value)
                        if name == 'location'
                        else T.input(type='text', name=name, value=str(value)))))

@ensure_csrf_cookie
def edit_event_template(django_request):

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    params = django_request.GET

    if 'event_template_name' not in params:
        return admin_error_page(django_request,
                                "Missing parameter",
                                "'event_template_name' not set in params")

    template_name = params['event_template_name']
    template_data = {key:"" for key in config_data['event_templates']['standard_fields']}
    template_data.update(model.database.find_event_template(template_name))
    form = [T.form(action=django.urls.reverse('makers_admin:save_template_edits'),
                   method='POST')[
        T.input(type="hidden",
                name="csrfmiddlewaretoken",
                value=django.middleware.csrf.get_token(django_request)),
        T.input(type='hidden',
                name='original_template_name',
                value=template_name),
        T.table[[T.tr[T.th(class_='ralabel')[name],
                      T.td[template_field(name, template_data[name])]]
                 for name in sorted(template_data.keys())],
                T.tr[T.td[""], T.td[T.input(type='submit', value="Save template")]]]]]

    page_data = model.pages.HtmlPage("Event template editor",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content(template_name + " event template",
                          form)
    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def save_template_edits(django_request):

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    params = django_request.POST

    if 'original_template_name' not in params:
        return admin_error_page(django_request,
                                "Missing parameter",
                                "'original_template_name' not set in params")

    template_name = params['event_template_name']
    base_template_name = params['original_template_name']

    template_data = model.database.find_event_template(template_name)
    template_data.update({key: value
                          for key, value in params.items()
                          if key not in ['original_template_name'
                                         # probably some system stuff to filter too
                                     ]})

    if template_name != base_template_name:
        print("Creating new template", template_name)
        del template_data['_id']
    else:
        print("Modifying existing template", template_name)

    database.save_event_template(template_data)

    page_data = model.pages.HtmlPage("Event template saved",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content("Event template " + template_name + " saved",
                          [T.p[str(template_data)]])
    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def backup_database(django_request):

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    params = django_request.GET

    # todo: fill in

    page_data = model.pages.HtmlPage("Database backup",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content("Unimplemented",
                          [T.p["This feature has not been written yet."]])
    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def gdpr_delete_user(django_request):

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    params = django_request.POST

    # todo: fill in

    page_data = model.pages.HtmlPage("",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content("",
                          [""])
    return HttpResponse(str(page_data.to_string()))

import django.core.mail

@ensure_csrf_cookie
def test_message(django_request):

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    params = django_request.POST

    subject = params['subject']
    body = params['message']
    recipient = params['to']

    sent = django.core.mail.send_mail(subject, body, "makers@makespace.org", [recipient])

    page_data = model.pages.HtmlPage("Message apparently sent" if sent > 0 else "Message apparently not sent",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content("Test stub",
                          [T.p["Message count ", str(sent), " may have been sent to ", recipient]])
    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def update_django(django_request):

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    params = django_request.POST
    include_non_members = params['include_non_members']

    people = person.Person.list_all_people() if include_non_members else person.Person.list_all_members()

    countdown = 12

    created = []
    for whoever in people:
        if whoever.login_name is None:
            name = whoever.name()
            name_parts = name.split(' ')
            login = make_login(name_parts[0], name_parts[1])
            create_django_user(login,
                               whoever.get_email(),
                               name_parts[0], name_parts[1],
                               whoever.link_id)
            whoever.login_name = login
            whoever.save()
            created.append(who)
            countdown -= 1
            if countdown == 0:
                break

    page_data = model.pages.HtmlPage("Created django users",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content("Django user creation",
                          T.table[T.thead[T.tr[T.th["Name"],
                                               T.th["login name"],
                                               T.th["email"]]],
                                  T.tbody[[[T.tr[T.th[newbie.name()],
                                                 T.td[newbie.login_name],
                                                 T.td[newbie.get_email()]]]
                                           for newbie in created]]])
    return HttpResponse(str(page_data.to_string()))
