# Stuff for talking to the rest of the server --- very prone to change when we get real

 import django.core.mail
 import configuration

def mailer(address, subject, text):
    """Send a message to an address."""
    with open("/tmp/mailings", 'w+') as outfile:
        outfile.write("\nTo: " + address
                      + "\nSubject: " + subject
                      + "\n\n" + text)
    return django.core.mail.send_mail(subject,
                                      text,
                                      model.configuration.get_config()['server']['password_reset_from_address'],
                                      [address] if isinstance(address, str) else address,
                                      fail_silently=False)

def generate_page(template, person, event):
    """Generate a web page from a template."""
    pass
