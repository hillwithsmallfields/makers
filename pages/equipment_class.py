#!/usr/bin/python

import sys
sys.path.append('../common')

from nevow import flat
from nevow import tags as T
import config
import database

def equipment_class(machine_class):
    page = T.html[T.head[T.title["Equipment class " + machine_class]],
                  T.body[T.h1["Equipment class " + machine_class]]]
    # todo: get data from config, and search database for users, owners, and trainers
    return flat.flatten(page)

def main():                     # for testing
    print equipment_status("CNC router")

if __name__ == "__main__":
    main()
