from django.http import HttpResponse

# Create your views here.

def public_index(request):
    """View function for listing the equipment types."""
    return HttpResponse("""
    <html>
    <head><title>Equipment types list placeholder</title></head>
    <body><h1>Equipment types list placeholder</h1>
    <p>This is where the list of equipment types will go.</p>
    </body>
    </html>
    """)
