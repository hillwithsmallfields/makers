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
            role_eqtys[role] = [ eqty_row(role_ty_dict[k]) for k in sorted(keys(role_ty_dict)) ]
    return [T.h2["Personal details"],
            T.div(_class="personaldetails")[
                T.table(_class="personaldetails")[
                    T.tr[T.th["Name"], T.td[who.name()]],
                    T.tr[T.Th["email"], T.td[who.get_email()]]
                # todo: address etc to go here
                ],
            T.h2["Availability"],
            T.div(_class="availability")[
                # todo: availability table to go here
                ],
            T.h2["Equipment responsibilities"],
            T.div(_class="responsibilities")[
                # todo: owner / trainer table to go here
                ],
            T.h2["Equipment trained on"],
            T.div(_class="trainedon")[
                # todo: list of equipment trained on to go here
                ]
            T.h2["Training requests"],
            T.div(_class="requested")[
                # todo: list of outstanding training requests to go here
                ]
            T.h2["Events I'm hosting"],
            T.div(_class="hostingevents")[
                # todo: list of events they're hosting to go here
                ],
            T.h2["Events signed up for"],
            T.div(_class="signedevents")[
                # todo: list of events signed up for to go here
                ],
            T.h2["Events I can sign up for"],
            T.div(_class+"availableevents")[
                # todo: list of available events to go here
                ],
            T.h2["API links"],
            T.div(_class="apilinks")[
                # todo: api links to go here
                ]]
