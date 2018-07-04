from django.http import HttpResponse

# Create your views here.

def public_index(request):
    """
    View function for the landing page.
    """
    # based on https://docs.djangoproject.com/en/2.0/topics/http/views/
    return HttpResponse("""
    <html>
    <head><title>Public page placeholder</title></head>
    <body><h1>Public page placeholder</h1>
    <p>This is where the public landing page will go, with a login box.</p>
    <h2>Path</h2>
    <pre>"""
                        + ':'.join(sys.path)
                        + """</pre>
    </body>
    </html>
    """)
