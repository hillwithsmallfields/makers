from nevow import flat
from nevow import tags as T

import database
import pages

def member_row(person):
    name = person['given_name'] + " " + person['surname']
    return [T.tr[T.th(_class="pn")[name],
                 T.td(_class="em")[person['email']]]]

def list_members(viewing_member):
    """List all the members.
    Probably only the admins should be allowed to do this."""
    # todo: check that viewing_member is an admin
    members = database.members()
    # todo: get the names, sort them, construct a table
    # todo: allow the sorting to be by membership number, first name, or last name
    return T.table[[member_row(person) for person in database.members()]]
