#!/usr/bin/python

from nevow import flat
from nevow import tags as T
import configuration
import database
import pages

def member_profile(person, person_viewing):
    """Show a person profile, with fields appropriate to that person and this viewer."""
    if isinstance(person, basestring):
        person = get_person(person)
    if isinstance(person_viewing, basestring):
        person_viewing = get_person(person_viewing)
    if (person == person_viewing
        or database.is_administrator(person_viewing)):
        name = person['given_name'] + " " + person['family_name']
        return pages.page_string("Profile for " + name,
                                 [])
    else:
        return pages.error_page("You do not have permission to view this data")
