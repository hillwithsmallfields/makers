from nevow import flat
from nevow import tags as T

def member_profile():
    page = T.html[T.head[T.title["Profile for " + member.name]],
                  T.body[T.h1["Profile for " + member.name]]]
    return flat.flatten(page)
