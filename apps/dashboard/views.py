from django.http import HttpResponse

from untemplate.throw_out_your_templates_p3 import htmltags as T
import sys
import model.configuration
import model.pages
import pages.user_list_page as user_list_page
import model.database
# import model.person as person
import pages.person_page
import model.person

# Create your views here.

def public_index(request, who=""):
    """
    View function for the landing page.
    """
    # based on https://docs.djangoproject.com/en/2.0/topics/http/views/

    # who_obj = person.find(who)

    config_data = model.configuration.get_config()
    org_conf = config_data['organization']

    model.database.database_init(config_data)

    pages.person_page.person_page_setup()

    page_data = model.pages.SectionalPage("User dashboard for " + who + str(request.user),
                                          # todo: put these into a central place, for use on most pages
                                          [T.ul[T.li[T.a(href=org_conf['home_page'])["Home"]],
                                                T.li[T.a(href=org_conf['wiki'])["Wiki"]],
                                                T.li[T.a(href=org_conf['forum'])["Forum"]]]])

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

    # return HttpResponse("""
    # <html>
    # <head><title>Public page placeholder</title></head>
    # <body><h1>Public page placeholder for """ + who + """</h1>
    # <p>This is where the public landing page will go, with a login box.</p>
    # <h2>Path</h2>
    # <pre>"""
    #                     + ':'.join(sys.path)
    # + """
    # </pre>
    # <h2>Configuration</h2>
    # <pre>""" + str(config_data)
    # + """
    # </pre>    </body>
    # </html>
    # """)
