#!/usr/bin/python

import sys
sys.path.append('../common')

from nevow import flat
from nevow import tags as T
import config
import database

def event_calendar():
    page = T.html[T.head[T.title["Event calendar"]],
                  T.body[T.h1["Event calendar"]]]
    return flat.flatten(page)

def main():                     # for testing
    print event_calendar()

if __name__ == "__main__":
    main()
