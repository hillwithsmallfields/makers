from untemplate.throw_out_your_templates_p3 import htmltags as T
from django.http import HttpResponse
from datetime import datetime
import model.database           # for announcements and notifications; I should probably wrap them so apps don't need to see model.database
import model.equipment_type
import model.event
import model.pages
import model.person
import pages.event_page
import pages.person_page
from django.views.decorators.csrf import ensure_csrf_cookie

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
