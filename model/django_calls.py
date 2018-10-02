# Functions, associated with the model classes, that call django directly.

# They're in a separate file to make it easier to use the model
# classes outside our django apps (in particular, in the importer,
# which runs from the command line).

import model.person
import django.contrib.auth.forms

# account access

def send_password_reset_email(who):
    # based on https://stackoverflow.com/questions/5594197/trigger-password-reset-email-in-django-without-browser
    form = django.contrib.auth.forms.PasswordResetForm({'email': who.get_email()})
    form.is_valid()
    form.save()
