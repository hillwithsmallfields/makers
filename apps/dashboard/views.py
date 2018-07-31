from django.http import HttpResponse
from pages import page_pieces
from untemplate.throw_out_your_templates_p3 import htmltags as T
import model.configuration
import model.database
import model.pages
import model.person
import model.person as person
import pages.person_page
import pages.user_list_page
import sys
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def all_user_list_page(request):

    config_data = model.configuration.get_config()

    model.database.database_init(config_data)

    pages.person_page.person_page_setup()

    if request.user.is_anonymous:
        return HttpResponse("""<html><head><title>Error</title></head>
        <body><h1>Information not publicly available</h1>
        <p>The user list is not publicly visible.
        To see this, you must <a href="../users/login">login</a> as a user with admin rights.</p>
        </body></html>""")

    viewing_user = model.person.Person.find(request.user.link_id)

    page_data = model.pages.HtmlPage("User list page",
                                     pages.page_pieces.top_navigation(request),
                                     django_request=request)

    if viewing_user.is_administrator() or viewing_user.is_auditor():
        page_data.add_content("User list",
                              pages.user_list_page.user_list_section())
    else:
        page_data.add_content("Error", [T.p["You do not have permission to view the list of users."]])

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def dashboard_page(request, who=""):
    """
    View function for the landing page.
    """
    # based on https://docs.djangoproject.com/en/2.0/topics/http/views/

    config_data = model.configuration.get_config()

    model.database.database_init(config_data)

    pages.person_page.person_page_setup()

    if request.user.is_anonymous:
        return HttpResponse("""<html><head><title>This will be the public page</title></head>
        <body><h1>This will be the public page</h1>

        <p>It should display general status, and <a
        href="../users/login">login</a> and <a
        href="../users/signup">signup</a> boxes.</p> </body></html>""")

    viewing_user = model.person.Person.find(request.user.link_id)

    if who == "":
        subject_user = viewing_user
    else:
        # todo: remove this dirty hack for early debugging
        if True or viewing_user.is_administrator() or viewing_user.is_auditor():
            subject_user = model.person.Person.find(who)
        else:
            page_data = model.pages.HtmlPage("Error",
                                             pages.page_pieces.top_navigation(request),
                                             django_request=request)
            page_data.add_content("Error", [T.p["You do not have permission to view other users."]])
    if subject_user is None:
        page_data = model.pages.HtmlPage("Error",
                                         pages.page_pieces.top_navigation(request),
                                         django_request=request)
        page_data.add_content("Error", [T.p["Could not find the user " + who + "."]])
    else:
        page_data = model.pages.SectionalPage("User dashboard for " + subject_user.name(),
                                              pages.page_pieces.top_navigation(request),
                                              django_request=request)
        pages.person_page.add_person_page_contents(page_data, subject_user, viewing_user, request)

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def user_match_page(request, pattern):

    config_data = model.configuration.get_config()

    model.database.database_init(config_data)

    pages.person_page.person_page_setup()

    if request.user.is_anonymous:
        return HttpResponse("""<html><head><title>Error</title></head>
        <body><h1>Information not publicly available</h1>
        <p>The user list is not publicly visible.
        To see this, you must <a href="../users/login">login</a> as a user with admin rights.</p>
        </body></html>""")

    viewing_user = model.person.Person.find(request.user.link_id)

    page_data = model.pages.HtmlPage("Matching user list page",
                                     pages.page_pieces.top_navigation(request),
                                     django_request=request)

    if viewing_user.is_administrator() or viewing_user.is_auditor():
        page_data.add_content("User list",
                              pages.user_list_page.user_list_matching_section(pattern, False))
    else:
        page_data.add_content("Error", [T.p["You do not have permission to view the list of users."]])

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def update_mugshot(request):
    params = request.POST
    who = model.person.Person.find(params['subject_user_uuid'])
    admin_user = model.person.Person.find(request.user)
    # todo: update photo from upload
    return HttpResponse(pages.person_page.person_page_contents(who, admin_user,
                                                               extra_top_header="Confirmation",
                                                               extra_top_body=T.p["Mugshot updated."]).to_string)

@ensure_csrf_cookie
def update_profile(request):
    params = request.POST
    who = model.person.Person.find(params['subject_user_uuid'])
    admin_user = model.person.Person.find(request.user)
    who.update_profile(params)
    return HttpResponse(pages.person_page.person_page_contents(who, admin_user,
                                                               extra_top_header="Confirmation",
                                                               extra_top_body=T.p["Profile updated."]).to_string)
