# Functions, associated with the model classes, that call django directly.

# They're in a separate file to make it easier to use the model
# classes outside our django apps (in particular, in the importer,
# which runs from the command line).

import model.configuration
import model.person
import django.contrib.auth.forms

# for debug

from django.conf import settings

# account access

def send_password_reset_email(who, django_request):
    # based on https://stackoverflow.com/questions/5594197/trigger-password-reset-email-in-django-without-browser

    from_email = model.configuration.get_config()['server']['password_reset_from_address']
    to_email = who.get_email()
    print("email host is", settings.EMAIL_HOST, "and port is", settings.EMAIL_PORT, "and user is", settings.EMAIL_HOST_USER, "and from_email is", from_email, "and to_email would be", to_email)
    form = django.contrib.auth.forms.PasswordResetForm({'email': to_email})
    form.is_valid()
    form.save(from_email=from_email, request=django_request)
