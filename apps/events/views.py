from django.http import HttpResponse

# Create your views here.

def public_index(request):
    """View function for listing the events."""
    return HttpResponse("""
    <html>
    <head><title>Events list placeholder</title></head>
    <body><h1>Events list placeholder</h1>
    <p>This is where the list of events will go.</p>
    </body>
    </html>
    """)

def new_event(request):
    """View function for creating an event."""
    params = django_request.POST # when, submitter, event_type, and anything app-specific: such as: role, equiptype

    ev = event.Event.instantiate_template(params['event_type'],
                                          [params['equiptype']],
                                          [params['submitter']],
                                          params['when'])
    ev.publish()
    
    return HttpResponse("""
    <html>
    <head><title>Event creation placeholder</title></head>
    <body><h1>Event creation placeholder</h1>
    <p>This is where the event creation confirmation will go.</p>
    </body>
    </html>
    """)
