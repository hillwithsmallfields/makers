from nevow import flat
from nevow import tags as T

def equipment_status():
    page = T.html[T.head[T.title["Status of " + machine.name]],
                  T.body[T.h1["Status of " + machine.name]]]
    return flat.flatten(page)
