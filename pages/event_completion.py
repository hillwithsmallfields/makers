#!/usr/bin/python

import sys
sys.path.append('../common')

from nevow import flat
from nevow import tags as T
import config

def event_completion(event, person_viewing):
    """Make an attendance form for an event."""
    page = T.html[T.head[T.title["Completion of " + event['name']]],
                  T.body[T.h1["Completion of " + event['name']]]]
    return flat.flatten(page)

def main():                     # for testing
    john = {'name': "John"}
    induction = {'name': "Induction"
    print event_completion(induction, john)

if __name__ == "__main__":
    main()
