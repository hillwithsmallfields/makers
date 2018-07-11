from django.http import HttpResponse

import sys
import model.configuration as configuration

# Create your views here.

def public_index(request):
    """
    View function for the landing page.
    """
    # based on https://docs.djangoproject.com/en/2.0/topics/http/views/
    config_data = configuration.get_config()
    return HttpResponse("""
    <html>
    <head><title>Public page placeholder</title></head>
    <body><h1>Public page placeholder</h1>
    <p>This is where the public landing page will go, with a login box.</p>
    <h2>Path</h2>
    <pre>"""
                        + ':'.join(sys.path)
    + """
    </pre>
    <h2>Configuration</h2>
    <pre>""" + str(config_data)
    + """
    </pre>    </body>
    </html>
    """)
