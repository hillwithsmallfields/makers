from django.http import HttpResponse
from pages import page_pieces
from untemplate.throw_out_your_templates_p3 import htmltags as T
import model.database
import model.equipment_type
import model.pages
import model.person
import pages.equipment_type_page
import pages.page_pieces

def public_index(request, eqty):
    """View function for listing the equipment types."""

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    viewing_user = model.person.Person.find(request.user.link_id)

    # todo: if eqty is None or "", show list of equipment types

    eq_type = model.equipment_type.Equipment_type.find(eqty)

    page_data = model.pages.HtmlPage(eq_type.name,
                                     pages.page_pieces.top_navigation(request))

    if eq_type is None:
        page_data.add_content("Error", [T.p["Could not find equipment type " + eqty]])
    else:
        page_data.add_content("Equipment type details", pages.equipment_type_page.equipment_type_section(eq_type, viewing_user, request))

    return HttpResponse(str(page_data.to_string()))
