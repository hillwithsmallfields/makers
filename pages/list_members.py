from nevow import flat
from nevow import tags as T

import database
import pages

def list_members(viewing_member):
    """List all the members.
    Probably only the admins should be allowed to do this."""
    # todo: check that viewing_member is an admin
    members = database.members()
    # todo: get the names, sort them, construct a table
    return []
