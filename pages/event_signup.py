#!/usr/bin/python

import sys
sys.path.append('../common')

from nevow import flat
from nevow import tags as T
import config

def event_signup(event, person_viewing):
    """Make a signup form for an event."""
    page = T.html[T.head[T.title["Signup for " + event['name']]],
                  T.body[T.h1["Signup for " + event['name']]]]
    return flat.flatten(page)

def main():                     # for testing
    john = {'name': "John"}
    induction = {'name': "Induction"
    print event_signup(induction, john)

if __name__ == "__main__":
    main()
