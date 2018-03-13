#!/usr/bin/python

import sys
sys.path.append('../common')

from nevow import flat
from nevow import tags as T
import config
import database

def equipment_status(machine, person_viewing):
    """Show a machine page.
If the person viewing the page is an owner, they will get a form to alter the status."""
    page = T.html[T.head[T.title["Status of " + machine['name']]],
                  T.body[T.h1["Status of " + machine['name']]]]
    return flat.flatten(page)

def main():                     # for testing
    john = database.get_person("John Sturdy")
    betsy = database.get_machine("Betsy")
    print equipment_status(betsy, john)

if __name__ == "__main__":
    main()
