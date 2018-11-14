from PIL import Image
from datetime import datetime
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from pages import page_pieces
# from resizeimage import resizeimage
from untemplate.throw_out_your_templates_p3 import htmltags as T
import model.configuration
import model.database
import model.django_calls
import model.pages
import model.person
import model.person as person
import os
import pages.person_page
import pages.user_list_page
import re
import sys
import tempfile
import uuid

def logged_in_only():
    return HttpResponse("""<html><head><title>Error</title></head>
    <body><h1>Information not publicly available</h1>
    <p>Other users' information, including the user list,
    is not publicly visible.
    To see this, you must <a href="../users/login">login</a>
    as a user with admin rights.</p>
    </body></html>""")

@ensure_csrf_cookie
def all_user_list_page(django_request):

    config_data = model.configuration.get_config()

    model.database.database_init(config_data)

    pages.person_page.person_page_setup()

    if django_request.user.is_anonymous:
        return logged_in_only()

    viewing_user = model.person.Person.find(django_request.user.link_id)

    page_data = model.pages.HtmlPage("User list page",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)

    if viewing_user.is_administrator() or viewing_user.is_auditor():
        page_data.add_content("User list",
                              pages.user_list_page.user_list_section(django_request))
    else:
        page_data.add_content("Error", [T.p["You do not have permission to view the list of users."]])

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def dashboard_page(django_request, who=""):
    """
    View function for the landing page.
    """
    # based on https://docs.djangoproject.com/en/2.0/topics/http/views/

    config_data = model.configuration.get_config()

    model.database.database_init(config_data)

    pages.person_page.person_page_setup()

    if django_request.user.is_anonymous:
        return logged_in_only()

    viewing_user = model.person.Person.find(django_request.user.link_id)

    if who == "":
        subject_user = viewing_user
    else:
        if viewing_user.is_administrator() or viewing_user.is_auditor():
            subject_user = model.person.Person.find(who)
        else:
            page_data = model.pages.HtmlPage("Error",
                                             pages.page_pieces.top_navigation(django_request),
                                             django_request=django_request)
            page_data.add_content("Error", [T.p["You do not have permission to view other users."]])
            return HttpResponse(str(page_data.to_string()))
    if subject_user is None:
        page_data = model.pages.HtmlPage("Error",
                                         pages.page_pieces.top_navigation(django_request),
                                         django_request=django_request)
        page_data.add_content("Error", [T.p["Could not find the user " + who + "."]])
    else:
        page_data = model.pages.SectionalPage("User dashboard for " + subject_user.name(),
                                              pages.page_pieces.top_navigation(django_request),
                                              django_request=django_request)
        pages.person_page.add_person_page_contents(page_data, subject_user, viewing_user, django_request)

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def one_section(django_request, data_function, title, who=""):
    """
    View function for a single part of the user dashboard page.
    Intended for loading tabs on demand, Ajax-style.
    """

    config_data = model.configuration.get_config()

    model.database.database_init(config_data)

    pages.person_page.person_page_setup()

    if django_request.user.is_anonymous:
        return HttpResponse("""<html><head><title>This will be the public page</title></head>
        <body><h1>This will be the public page</h1>

        <p>It should display general status, and <a
        href="../users/login">login</a> and <a
        href="../users/signup">signup</a> boxes.</p> </body></html>""")

    viewing_user = model.person.Person.find(django_request.user.link_id)

    if who == "":
        subject_user = viewing_user
    else:
        if viewing_user.is_administrator() or viewing_user.is_auditor():
            subject_user = model.person.Person.find(who)
        else:
            page_data = model.pages.HtmlPage("Error",
                                             pages.page_pieces.top_navigation(django_request),
                                             django_request=django_request)
            page_data.add_content("Error", [T.p["You do not have permission to view other users."]])
            return HttpResponse(str(page_data.to_string()))
    if subject_user is None:
        page_data = model.pages.HtmlPage("Error",
                                         pages.page_pieces.top_navigation(django_request),
                                         django_request=django_request)
        page_data.add_content("Error", [T.p["Could not find the user " + who + "."]])
    else:
        page_data = model.pages.PageSection(title,
                                            [data_function(subject_user, viewing_user, django_request)],
                                            django_request=django_request)

    return HttpResponse(str(page_data.to_string()))

def profile_only(django_request, who=""):
    return one_section(django_request,
                       pages.person_page.profile_section,
                       "User profile",
                       who)

def notifications_only(django_request, who=""):
    return one_section(django_request,
                       pages.person_page.notifications_section,
                       "Notifications and announcements",
                       who)

def responsibilities_only(django_request, who=""):
    return one_section(django_request,
                       pages.person_page.responsibilities_section,
                       "Equipment responsibilities",
                       who)

def trained_on_only(django_request, who=""):
    print("Getting equipment I can use") # to see when it's done when loading lazily; todo: remove this print
    return one_section(django_request,
                       pages.person_page.equipment_trained_on_section,
                       "Equipment trained on",
                       who)

def other_equipment_only(django_request, who=""):
    return one_section(django_request,
                       pages.person_page.other_equipment_section,
                       "Other equipment",
                       who)

def training_requests_only(django_request, who=""):
    return one_section(django_request,
                       pages.person_page.training_requests_section,
                       "Outstanding training requests",
                       who)

def events_hosting_only(django_request, who=""):
    return one_section(django_request,
                       pages.person_page.events_hosting_section,
                       "Events I will be hosting",
                       who)

def events_attending_only(django_request, who=""):
    return one_section(django_request,
                       pages.person_page.events_attending_section,
                       "Events I have signed up for",
                       who)

def events_hosted_only(django_request, who=""):
    return one_section(django_request,
                       pages.person_page.events_hosted_section,
                       "Events I have hosted",
                       who)

def events_attended_only(django_request, who=""):
    return one_section(django_request,
                       pages.person_page.events_attended_section,
                       "Events I have attended",
                       who)

def events_available_only(django_request, who=""):
    return one_section(django_request,
                       pages.person_page.events_available_section,
                       "Events I can sign up for",
                       who)

def admin_only(django_request, who=""):
    return one_section(django_request,
                       pages.person_page.admin_section,
                       "Admin actions",
                       who)

@ensure_csrf_cookie
def user_match_page(django_request, pattern):

    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    params = django_request.GET
    if 'pattern' in params:
        pattern = params['pattern']

    pages.person_page.person_page_setup()

    if django_request.user.is_anonymous:
        return logged_in_only()

    viewing_user = model.person.Person.find(django_request.user.link_id)

    page_data = model.pages.HtmlPage("Matching user list page",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)

    if viewing_user.is_administrator() or viewing_user.is_auditor():
        page_data.add_content("User list",
                              pages.user_list_page.user_list_matching_section(django_request, pattern, False))
    else:
        page_data.add_content("Error", [T.p["You do not have permission to view the list of users."]])

    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def update_mugshot(django_request):
    # I think https://simpleisbetterthancomplex.com/tutorial/2017/08/01/how-to-setup-amazon-s3-in-a-django-project.html may tell me what to do with the saved pictures
    config_data = model.configuration.get_config()
    mugshot_config = config_data['mugshots']
    model.database.database_init(config_data)

    params = django_request.POST
    who = model.person.Person.find(params['subject_user_uuid'])

    mugshot = django_request.FILES['mugshot']

    # todo: put these on S3
    directory = mugshot_config['directory']
    if not os.path.isdir(directory):
        os.makedirs(directory)
    mugshot_filename = os.path.join(directory,
                                    ('uploaded_' # todo: also have 'verified_' photos
                                     + str(uuid.uuid4()) + ".jpg"))

    with tempfile.TemporaryFile() as incoming_image_file:
        for chunk in mugshot.chunks():
            incoming_image_file.write(chunk)
            incoming_image_file.seek(0)
            with Image.open(incoming_image_file) as image:
                # resized_image = resizeimage.resize_contain(image,
                #                                            [int(mugshot_config['width']),
                #                                             int(mugshot_config['height'])])
                # resized_image.save(mugshot_filename)
                image.save(mugshot_filename)

    who.set_profile_field('mugshot', mugshot_filename)

    page_data = model.pages.HtmlPage("Confirmation",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content("Confirmation", [T.p["Photo updated."]])
    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def update_profile(django_request):
    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    params = django_request.POST
    who = model.person.Person.find(params['subject_user_uuid'])

    who.update_profile(params, django_request)

    page_data = model.pages.HtmlPage("Confirmation",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content("Confirmation", [T.p["Profile updated."]])
    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def update_configured_profile(django_request):
    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    params = django_request.POST
    who = model.person.Person.find(model.pages.unstring_id(params['subject_user_uuid']))

    if who is None:
        page_data = model.pages.HtmlPage("Error",
                                         pages.page_pieces.top_navigation(django_request),
                                         django_request=django_request)
        page_data.add_content("Error", [T.p["Could not find user identified by "
                                            + str(params['subject_user_uuid'])]])
        return HttpResponse(str(page_data.to_string()))

    who.update_configured_profile(params)
    page_data = model.pages.HtmlPage("Confirmation",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content("Confirmation", [T.p["Profile updated."]])
    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def update_site_controls(django_request):
    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    params = django_request.POST
    who = model.person.Person.find(model.pages.unstring_id(params['subject_user_uuid']))

    who.update_controls(params)

    page_data = model.pages.HtmlPage("Confirmation",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content("Confirmation", [T.p["Controls updated."]])
    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def update_availability(django_request):
    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    day_names = config_data['timeslots']['days']
    slot_names = ['Morning', 'Afternoon', 'Evening', 'Other']

    params = django_request.POST
    who = model.person.Person.find(model.pages.unstring_id(params['person']))
    if who is None:
        page_data = model.pages.HtmlPage("Error",
                                         pages.page_pieces.top_navigation(django_request),
                                         django_request=django_request)
        page_data.add_content("Error", [T.p["Person not found"]])
        return HttpResponse(str(page_data.to_string()))

    available_bits = 0

    # these come through as things like 'Saturday_Afternoon': 'on', just for the ones that are on; the others are omitted
    # todo: on changing availability, re-run invite_available_interested_people on the equipment types for which this person has a training request outstanding
    for slot, setting in params.items():
        if setting != 'on':
            continue
        if '_' not in slot:
            continue
        day_of_week, time_of_day = slot.split('_')
        if day_of_week not in day_names:
            print("bad day name", day_of_week, "not in", day_names)
            continue
        day_number = day_names.index(day_of_week)
        if time_of_day not in slot_names:
            print("bad slot name", time_of_day, "not in", slot_names)
            continue
        slot_number = slot_names.index(time_of_day)
        available_bits |= 1 << (day_number * 4 + slot_number)

    who.available = available_bits
    who.save()

    page_data = model.pages.HtmlPage("Confirmation",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content("Confirmation", [T.p["Availability updated."]])
    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def update_levels(django_request):
    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    params = django_request.POST
    who = model.person.Person.find(model.pages.unstring_id(params['subject_user_uuid']))

    interests = who.get_interests()
    interests.update({topic: int(level)
                      for topic, level in params.items()
                      if re.match("[0-9]+", level)})
    who.set_interests(interests)

    interest_emails = [False] * 4
    for lev in range(1,4):
        if 'mail_'+str(lev) in params:
            interest_emails[lev] = True
    who.set_profile_field('interest_emails', interest_emails)

    page_data = model.pages.HtmlPage("Confirmation",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content("Confirmation", [T.p["Interests updated."]])
    return HttpResponse(str(page_data.to_string()))

@ensure_csrf_cookie
def update_avoidances(django_request):
    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    params = django_request.POST
    who = model.person.Person.find(model.pages.unstring_id(params['subject_user_uuid']))

    who.update_avoidances(params)

    page_data = model.pages.HtmlPage("Confirmation",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content("Confirmation", [T.p["Dietary info updated."]])
    return HttpResponse(str(page_data.to_string()))

def person_from_request(django_request):
    return model.person.Person.find(
        model.pages.unstring_id(
            django_request.POST['subject_user_uuid']))

def reset_messages(django_request):
    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    who = person_from_request(django_request)

    who.notifications_read_to = datetime(1970, 1, 1)
    who.announcements_read_to = datetime(1970, 1, 1)
    who.save()

    page_data = model.pages.HtmlPage("Confirmation",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content("Confirmation", [T.p["Messages reset."]])
    return HttpResponse(str(page_data.to_string()))

def announcements_read(django_request):
    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    person_from_request(django_request).mark_announcements_read()

    page_data = model.pages.HtmlPage("Confirmation",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content("Confirmation", [T.p["Messages marked as read."]])
    return HttpResponse(str(page_data.to_string()))

def notifications_read(django_request):
    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    person_from_request(django_request).mark_notifications_read()

    page_data = model.pages.HtmlPage("Confirmation",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content("Confirmation", [T.p["Messages marked as read."]])
    return HttpResponse(str(page_data.to_string()))

def send_password_reset(django_request):
    config_data = model.configuration.get_config()
    model.database.database_init(config_data)

    who = person_from_request(django_request)
    recipient = who.get_email()

    model.django_calls.send_password_reset_email(who,
                                                 django_request)

    page_data = model.pages.HtmlPage("Password reset confirmation",
                                     pages.page_pieces.top_navigation(django_request),
                                     django_request=django_request)
    page_data.add_content("Confirmation",
                          [T.p[("Password reset sent to " + who.name()
                                + " <", T.a(href="mailto:"+recipient)[recipient], ">.")]])

    return HttpResponse(str(page_data.to_string()))
