#!/usr/bin/python

import sys
sys.path.append('../common')

from nevow import flat
from nevow import tags as T
import config
import pages

def event_completion(event, person_viewing):
    """Make an attendance form for an event."""
    # todo: generate attendance form
    return pages.page_string("Completion of " + event['name'],
                             [])

def main():                     # for testing
    john = {'name': "John"}
    induction = {'name': "Induction"
    print event_completion(induction, john)

if __name__ == "__main__":
    main()
