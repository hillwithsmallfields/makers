from nevow import flat
from nevow import tags as T

import person

def eqty_row(ty):
    return ty                   # todo: create a row from this

def person_page_contents(who, viewer):
    role_eqtys = {}
    for role in ['user', 'owner', 'trainer']:
        role_types = who.get_equipment_types(role)
        if len(role_types) > 0:
            role_ty_dict = { ty.name.replace('_', ' ').capitalize(): ty
                             for ty in role_types }
            role_eqtys[role] = [ eqty_row(role_ty_dict[k]) for k in sorted(role_ty_dict.keys()) ]
    return [T.h2["Personal details"],
            T.div(class_="personaldetails")[
                T.table(class_="personaldetails")[
                    T.tr[T.th["Name"], T.td[who.name()]],
                    T.tr[T.th["email"], T.td[who.get_email()]],
                    "todo: address etc to go here"
                ],
            T.h2["Availability"],
                T.div(class_="availability")[
                    "todo: availability table to go here"
                ],
            T.h2["Equipment responsibilities"],
                T.div(class_="responsibilities")[
                    "todo: owner / trainer table to go here"
                ],
            T.h2["Equipment trained on"],
                T.div(class_="trainedon")[
                    "todo: list of equipment trained on to go here"
                ],
            T.h2["Training requests"],
                T.div(class_="requested")[
                    "todo: list of outstanding training requests to go here"
                ],
            T.h2["Events I'm hosting"],
                T.div(class_="hostingevents")[
                    "todo: list of events they're hosting to go here"
                ],
            T.h2["Events signed up for"],
                T.div(class_="signedevents")[
                    "todo: list of events signed up for to go here"
                ],
            T.h2["Events I can sign up for"],
                T.div(class_="availableevents")[
                    "todo: list of available events to go here"
                ],
            T.h2["API links"],
                T.div(class_="apilinks")[
                    "todo: api links to go here"
                ]]]
