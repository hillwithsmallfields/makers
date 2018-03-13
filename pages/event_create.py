#!/usr/bin/python

import sys
sys.path.append('../common')

from nevow import flat
from nevow import tags as T
import config
import database

def event_create(person_making):
    """Make an event."""
    page = T.html[T.head[T.title["Create event"]],
                  T.body[T.h1["Create event"]]]
    return flat.flatten(page)

def main():                     # for testing
    john = database.get_person("John Sturdy")
    print event_create()

if __name__ == "__main__":
    main()
