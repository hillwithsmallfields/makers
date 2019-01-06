# Functions, associated with the model classes, that call django directly.

# They're in a separate file to make it easier to use the model
# classes outside our django apps (in particular, in the importer,
# which runs from the command line).

import model.configuration
import model.database
import model.person
import model.times
import uuid
import django.contrib.auth.forms
from users.models import CustomUser

# for debug

from django.conf import settings

# account access

def send_password_reset_email(who, django_request):
    # based on https://stackoverflow.com/questions/5594197/trigger-password-reset-email-in-django-without-browser

    config = model.configuration.get_config('server')
    from_email = config['password_reset_from_address']
    to_email = who.get_email()
    django_user = model.database.person_get_django_user_data(who)
    if django_user:
        django_user.last_login = model.times.now()
        if not django_user.has_usable_password():
            django_user.set_password(uuid.uuid4())
        django_user.save()
    print("Sending password reset to", to_email)
    domain = config['domain']
    form = django.contrib.auth.forms.PasswordResetForm(
        {'email': to_email,
         'use_https': True
        })
    form.is_valid()
    form.save(from_email=from_email,
              domain_override=domain,
              request=django_request)

send_creation_email = False

def create_django_user(login_name, email,
                       given_name, surname,
                       link_id,
                       django_request=None):
    # based on https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Authentication
    # Create user and save to the database
    print("create_django_user creating django_user")
    try:
        django_user = CustomUser.objects.create_user(login_name, email, '')
    except:
        return False

    # Update fields and then save again
    django_user.first_name = given_name
    django_user.last_name = surname
    django_user.link_id = link_id
    print("create_django_user setting unknown password")
    django_user.set_password(uuid.uuid4())
    print("create_django_user saving data")
    django_user.save()
    if send_creation_email and django_request:
        print("create_django_user sending email")
        model.django_calls.send_password_reset_email(
            model.person.Person.find(link_id),
            django_request)
    print("create_django_user complete")
    return True

def django_password_is_usable(who):
    django_user = model.database.person_get_django_user_data(who)
    return django_user and django_user.has_usable_password()

def django_user_is_active(who):
    django_user = model.database.person_get_django_user_data(who)
    return django_user and django_user.is_active

def django_user_activation(who, active):
    django_user = model.database.person_get_django_user_data(who)
    django_user.is_active = active
    django_user.save()

def django_user_is_staff(who):
    django_user = model.database.person_get_django_user_data(who)
    return django_user and django_user.is_staff
