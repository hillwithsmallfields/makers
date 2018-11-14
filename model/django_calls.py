# Functions, associated with the model classes, that call django directly.

# They're in a separate file to make it easier to use the model
# classes outside our django apps (in particular, in the importer,
# which runs from the command line).

import model.configuration
import model.person
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

def create_django_user(login_name, email,
                       given_name, surname,
                       link_id,
                       django_request=None):
    # based on https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Authentication
    # Create user and save to the database
    print("create_django_user creating django_user")
    django_user = CustomUser.objects.create_user(login_name, email, '')

    # Update fields and then save again
    django_user.first_name = given_name
    django_user.last_name = surname
    django_user.link_id = link_id
    print("create_django_user setting unusable password")
    django_user.set_unusable_password()
    print("create_django_user saving data")
    django_user.save()
    if django_request:
        print("create_django_user sending email")
        model.django_calls.send_password_reset_email(
            model.person.Person.find(link_id),
            django_request)
    print("create_django_user complete")
