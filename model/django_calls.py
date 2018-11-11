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
