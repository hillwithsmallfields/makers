from nevow import flat
from nevow import tags as T
import config

def member_profile(person, person_viewing):
    """Show a person profile, with fields appropriate to that person and this viewer."""
    page = T.html[T.head[T.title["Profile for " + person['name']]],
                  T.body[T.h1["Profile for " + person['name']]]]
    return flat.flatten(page)
