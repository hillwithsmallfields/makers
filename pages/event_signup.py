#!/usr/bin/python

from nevow import flat
from nevow import tags as T
import configuration
import pages

def event_signup(event, person_viewing):
    """Make a signup form for an event."""
    # todo: make signup data
    return pages.page_string("Signup for " + event['name'],
                             [])
