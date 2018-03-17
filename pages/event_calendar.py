#!/usr/bin/python

from nevow import flat
from nevow import tags as T
import configuration
import database
import pages

def event_calendar():
    # todo: generate calendar
    return pages.page_string("Event calendar",
                             [])
