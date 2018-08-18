from datetime import datetime
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from untemplate.throw_out_your_templates_p3 import htmltags as T
import django.urls
import model.database           # for announcements and notifications; I should probably wrap them so apps don't need to see model.database
import model.equipment_type
import model.event
import model.pages
import model.person
import pages.event_page
import pages.person_page

@ensure_csrf_cookie
def create_event(django_request):

    """The first stage of event creation.
    This sets up the parameters based on the event template."""

    base = django_request.scheme + "://" + django_request.META['HTTP_HOST']
    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    template_name = django_request.GET['template_name']
    equipment_type = django_request.GET.get('equipment_type', "")

    template = model.event.Event.find_template(template_name)

    page_data = model.pages.HtmlPage("Create event",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)

    form = T.form(action=base+"/makers_admin/create_event_2",
                  method='POST')[T.table[T.tr[T.th["When"], T.td[T.input(type='datetime', name='start')]],
                                         [[T.tr[T.th(class_="ralabel")[k.replace('_', ' ').capitalize()],
                                                T.td[T.input(type='text',
                                                             name=k,
                                                             value=str(template[k]).replace('$equipment',
                                                                                            equipment_type))]]]
                                          for k in sorted(template.keys())
                                          if k != '_id'],
                                         T.tr[T.td[""], T.td[T.input(type='submit', value="Create event")]]]]

    page_data.add_content("Event creation form", form)
    return HttpResponse(str(page_data.to_string()))

def create_event_2(django_request):

    """The second stage of event creation."""

    base = django_request.scheme + "://" + django_request.META['HTTP_HOST']
    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    params = django_request.POST

    # todo: create an event, and 'update' the params onto its __dict__, with appropriate type conversions (including of the lists of conditions etc)

    page_data = model.pages.HtmlPage("Create event",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)

    result = "placeholder"

    page_data.add_content("Event creation confirmation", result)
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

    """Send an announcement to everyone."""

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

def make_login(given_name, surname):
    login_base = ((given_name[:3] if len(given_name) > 3 else given_name)
                  + (surname[:3] if len(surname) > 3 else surname))
    # todo: look for the lowest number that is unused so far for this login_base
    return login_base + "1"

def create_django_user(login_name, email, given_name, surname, link_id):
    # based on https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Authentication
    # Create user and save to the database
    django_user = User.objects.create_user(login_name, email, '')

    # Update fields and then save again
    django_user.first_name = given_name
    django_user.last_name = surname
    django_user.link_id = link_id
    django_user.set_unusable_password()
    django_user.save()
    model.person.Person.find(link_id).send_password_reset_email(user)

@ensure_csrf_cookie
def add_user(django_request):

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    params = django_request.POST
    given_name = params['given_name']
    surname = params['surname']
    email = params['email']
    login = make_login(given_name, surname)
    induction_event = None

    link_id = model.database.add_person({'membership_number': member_no,
                                         'email': row['Email'],
                                         'given_name': name_parts[0],
                                         'surname': name_parts[1],
                                         'known_as': name_parts[0]},
                                        {'membership_number': member_no})
    create_django_user(login, email, given_name, surname, link_id)

    if params['inducted']:
        induction_id = params.get('induction_event', None)
        induction_event = model.event.Event.find(model.pages.unstring_id(induction_id)) if induction_id else None
        if induction_event is None:
            induction_event = model.event.Event(configuration.get_config()['organization']['name'] + " training",
                                                datetime.utcnow(),
                                                [model.person.Person.find(django_request.user.link_id)._id])
        induction_event.mark_results([model.person.Person.find(link_id)], [], [])

    page_data = model.pages.HtmlPage("Added user",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content("Confirmation of adding user " + given_name + " " + surname,
                          [T.h2["Add another user"],
                           pages.person_page.add_user_form(django_request,
                                                           induction_event._id)])
    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def update_django(django_request):

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    params = django_request.POST
    include_non_members = params['include_non_members']

    people = person.Person.list_all_people() if include_non_members else person.Person.list_all_members()

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
