from django.http import HttpResponse

from untemplate.throw_out_your_templates_p3 import htmltags as T
import sys
import model.configuration as configuration
import model.pages as pages
import pages.user_list_page as user_list_page
import model.database
# import model.person as person

# Create your views here.

def public_index(request, who=""):
    """
    View function for the landing page.
    """
    # based on https://docs.djangoproject.com/en/2.0/topics/http/views/

    # who_obj = person.find(who)

    config_data = configuration.get_config()
    org_conf = config_data['organization']

    model.database.database_init(config_data)

    page_data = pages.SectionalPage("User dashboard for " + who + str(request.user),
                                    # todo: put these into a central place, for use on most pages
                                    [T.ul[T.li[T.a(href=org_conf['home_page'])["Home"]],
                                          T.li[T.a(href=org_conf['wiki'])["Wiki"]],
                                          T.li[T.a(href=org_conf['forum'])["Forum"]]]])

    if who == "":
        who = "unspecified user"

    if who == "all":
        page_data.add_section("User list",
                              user_list_page.user_list_section())

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
