from untemplate.throw_out_your_templates_p3 import htmltags as T
from django.http import HttpResponse
import model.equipment_type
import model.event
import model.pages
import model.person
import pages.event_page
import pages.person_page
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def create_event(django_request):

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    template_types = event.Event.list_templates([], [])

    page_data = model.pages.HtmlPage("Create event",
                                     pages.page_pieces.top_navigation(request),
                                     django_request=request)

    page_data.add_content("Event form",
                          T.ul[[T.li[str(tt)] for tt in template_types]])

    return HttpResponse(str(page_data.to_string()))
