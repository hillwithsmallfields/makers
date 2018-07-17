from django.http import HttpResponse
from pages import page_pieces
from untemplate.throw_out_your_templates_p3 import htmltags as T
import model.configuration
import model.database
import model.pages
import model.person
import model.person as person
import pages.person_page
import pages.user_list_page as user_list_page
import sys

def public_index(request, who=""):
    """
    View function for the landing page.
    """
    # based on https://docs.djangoproject.com/en/2.0/topics/http/views/

    config_data = model.configuration.get_config()

    model.database.database_init(config_data)

    pages.person_page.person_page_setup()

    page_data = model.pages.SectionalPage("User dashboard for " + who + str(request.user),
                                          pages.page_pieces.top_navigation())

    viewing_user = model.person.Person.find(request.user.link_id)
    if who == "all":
        if viewing_user.is_administrator() or viewing_user.is_auditor():
            page_data.add_section("User list",
                                  user_list_page.user_list_section())
        else:
            page_data.add_section("Error", [T.p["You do not have permission to view the list of users."]])
    else:
        if who == "":
            subject_user = viewing_user
        else:
            if viewing_user.is_administrator() or viewing_user.is_auditor():
                subject_user = model.person.Person.find(who)
            else:
                subject_user = None
                page_data.add_section("Error", [T.p["You do not have permission to view other users."]])
        if subject_user is None:
            page_data.add_section("Error", [T.p["Could not find the user " + who + "."]])
        else:
            pages.person_page.add_person_page_contents(page_data, subject_user, viewing_user)

    return HttpResponse(str(page_data.to_string()))
