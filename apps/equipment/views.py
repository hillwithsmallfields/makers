from django.http import HttpResponse

# Create your views here.

def public_index(request):
    """View function for listing the equipment."""
    return HttpResponse("""
    <html>
    <head><title>Equipment list placeholder</title></head>
    <body><h1>Equipment list placeholder</h1>
    <p>This is where the list of equipment will go.</p>
    </body>
    </html>
    """)
