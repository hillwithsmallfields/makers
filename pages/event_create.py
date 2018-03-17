#!/usr/bin/python

from nevow import flat
from nevow import tags as T
import configuration
import database
import pages

def event_create(person_making):
    """Make an event."""
    # todo: make the event creation data
    # This will use a template from the config
    return pages.page_string("Create event",
                             [])
