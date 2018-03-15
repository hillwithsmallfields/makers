#!/usr/bin/python

import sys
sys.path.append('../common')

from nevow import flat
from nevow import tags as T
import config
import database
import pages

def equipment_class(machine_class):
    # todo: get data from config, and search database for users, owners, and trainers
    return pages.page_string("Equipment class " + machine_class,
                             [])

def main():                     # for testing
    print equipment_class("CNC router")

if __name__ == "__main__":
    main()
