from nevow import flat
from nevow import tags as T
import config

def equipment_status(machine, person_viewing):
    """Show a machine page.
If the person viewing the page is an owner, they will get a form to alter the status."""
    page = T.html[T.head[T.title["Status of " + machine['name']]],
                  T.body[T.h1["Status of " + machine['name']]]]
    return flat.flatten(page)
