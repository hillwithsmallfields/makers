from django.http import HttpResponse
from pages import page_pieces
from untemplate.throw_out_your_templates_p3 import htmltags as T
import model.database
import model.machine
import model.pages
import model.person
import pages.machine_page
import pages.page_pieces

# Create your views here.

def public_index(request, machine):
    """View function for viewing a machine."""

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    page_data = model.pages.HtmlPage(eqty,
                                     pages.page_pieces.top_navigation())

    viewing_user = model.person.Person.find(request.user.link_id)

    mach = model.machine.find(machine)

    if mach is None:
        page_data.add_content("Error", [T.p["Could not find machine " + machine]])

    page_data.add_content("Machine", pages.machine_page.machine_section(mach))

    return HttpResponse(str(page_data.to_string()))
