#!/usr/bin/python

import sys
sys.path.append('../common')

from nevow import flat
from nevow import tags as T
import config
import database
import pages

def event_calendar():
    # todo: generate calendar
    return pages.page_string("Event calendar",
                             [])

def main():                     # for testing
    print event_calendar()

if __name__ == "__main__":
    main()
