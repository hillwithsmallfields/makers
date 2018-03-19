#!/usr/bin/python

from nevow import flat
from nevow import tags as T

import database
import pages

def equipment_status(machine, person_viewing):
    """Show a machine page.
If the person viewing the page is an owner, they will get a form to alter the status."""
    # todo: get equipment status
    return pages.page_string("Status of " + machine['name'],
                             [])

def main():                     # for testing
    john = database.get_person("Joe Bloggs")
    betsy = database.get_machine("Betsy")
    print equipment_status(betsy, john)

if __name__ == "__main__":
    main()
