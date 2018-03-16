#!/usr/bin/python

import sys
sys.path.append('../common')

from nevow import flat
from nevow import tags as T
import config
import database
import pages

def event_create(person_making):
    """Make an event."""
    # todo: make the event creation data
    # This will use a template from the config
    return pages.page_string("Create event",
                             [])

def main():                     # for testing
    john = database.get_person("John Sturdy")
    print event_create()

if __name__ == "__main__":
    main()
