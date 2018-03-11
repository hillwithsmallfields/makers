from nevow import flat
from nevow import tags as T
import config

def event_signup(event, person_viewing):
    """Make a signup form for an event."""
    page = T.html[T.head[T.title["Signup for " + event['name']]],
                  T.body[T.h1["Signup for " + event['name']]]]
    return flat.flatten(page)
