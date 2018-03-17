#!/usr/bin/python

from nevow import flat
from nevow import tags as T

import configuration
import pages

def event_completion(event, person_viewing):
    """Make an attendance form for an event."""
    # todo: generate attendance form
    return pages.page_string("Completion of " + event['name'],
                             [])
