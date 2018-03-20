from nevow import flat
from nevow import tags as T

import database
import pages

def member_row(person, viewing_person):
    name, nickname = database.person_name(person, viewing_person)
    return [T.tr[T.th(_class='pn')[name],
                 T.td(_class='nn')[nickname],
                 T.td(_class='em')[database.person_email(person, viewing_person)]]]

def list_members(viewing_person):
    """List all the members.
    Probably only the admins should be allowed to do this."""
    members = database.members()
    # todo: allow the sorting to be by membership number, date joined, first name, or last name
    return T.table[T.tr[T.th["Name"], T.th["Known as"], T.th["email"]],
                   [member_row(person, viewing_person)
                    for person in database.members()]]

def list_members_page(viewing_member):
    return pages.page_string("List of members",
                             list_members(viewing_member))
