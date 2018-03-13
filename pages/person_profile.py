#!/usr/bin/python

import sys
sys.path.append('../common')

from nevow import flat
from nevow import tags as T
import config
import database

def member_profile(person, person_viewing):
    """Show a person profile, with fields appropriate to that person and this viewer."""
    name = person['given_name'] + " " + person['family_name']
    page = T.html[T.head[T.title["Profile for " + name]],
                  T.body[T.h1["Profile for " + name]]]
    return flat.flatten(page)

def main():                     # for testing
    john = database.get_person('John Sturdy')
    print member_profile(john, john)

if __name__ == "__main__":
    main()
