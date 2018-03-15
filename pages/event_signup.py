#!/usr/bin/python

import sys
sys.path.append('../common')

from nevow import flat
from nevow import tags as T
import config
import pages

def event_signup(event, person_viewing):
    """Make a signup form for an event."""
    # todo: make signup data
    return pages.page_string("Signup for " + event['name'],
                             [])

def main():                     # for testing
    john = {'name': "John"}
    induction = {'name': "Induction"
    print event_signup(induction, john)

if __name__ == "__main__":
    main()
