from datetime import datetime, timedelta
from event import Event
import time

class Timeline(object):

    def __init__(self):
        self.events = []             # in time order, latest first

    def __str__(self):
        return "[" + " ".join(map(str, self.events)) + "]"

    def __repr__(self):
        return self.__str__()

    def insert(self, event):
        """Insert an event at its place in the timeline."""
        eventwhen = event.start
        events = self.events
        for i in range(0, len(events)):
            if events[i][0] < eventwhen:
                self.events.insert(i, (eventwhen, event))
                return
        self.events.insert(len(events), (eventwhen, event))

    def until(self, when):
        """Return all the events up to a given time."""
        events = self.events
        for i in range(0, len(events)):
            if events[i][0] < when:
                return events[i:]
        return []

    def since(self, when):
        """Return all the events since a given time."""
        events = self.events
        for i in range(0, len(events)):
            if events[i][0] < when:
                return events[:i]
        return events

    def between(self, begin, end):
        """Return all the events between two given times."""
        events = self.events
        for i in range(0, len(events)):
            if events[i][0] < end:
                for j in range(i, len(events)):
                    if events[j][0] < begin:
                        return events[i:j]
                return events[i:]
        return []

    def next(self, when,
             event_types=None,
             equipment=None,
             locations=None):
        """Return the next event matching the given criteria."""
        if when is None:
            when = datetime.now()
        events = self.events
        for i in range(0, len(events)):
            if events[i][0] < when:
                break
        for j in range(i, 0, -1):
            poss = events[j][1]
            if event_types and poss.event_type in event_types:
                if (equipment is None
                    or (poss.equipment is not None
                        and equipment in poss.equipment)):
                    return poss
            if locations and poss.location in locations:
                return poss
        return None

    def latest(self, when,
               event_types=None,
               equipment=None,
               locations=None):
        """Return the latest event matching the given criteria."""
        if when is None:
            when = datetime.now()
        events = self.events
        for i in range(0, len(events)):
            if events[i][0] < when:
                break
        for j in range(i, len(events)):
            poss = events[j][1]
            if event_types and poss.event_type in event_types:
                if (equipment is None
                    or (poss.equipment is not None
                        and equipment in poss.equipment)):
                    return poss
            if locations and poss.location in locations:
                return poss
        return None

def test_timelines():
    x = Timeline()
    day_0 = datetime(2017, 11, 12, 13, 14, 15)
    day_before_all = day_0 - timedelta(1)
    day_1 = day_0 + timedelta(1)
    day_2 = day_0 + timedelta(2)
    day_3 = day_0 + timedelta(3)
    day_4 = day_0 + timedelta(4)
    day_5 = day_0 + timedelta(5)
    day_6 = day_0 + timedelta(6)
    day_after_all = day_0 + timedelta(7)
    # these should appear in the order Joe, Jane, Arthur, John
    x.insert(Event('training', day_2, ['Jane Smith']))
    x.insert(Event('training', day_0, ['Arthur King'], equipment=['laser']))
    x.insert(Event('meeting', day_4, ['Joe Bloggs']))
    x.insert(Event('training', day_6, ['John Doe']))
    print "Timeline is now", x
    r1 = x.until(day_before_all)
    print len(r1), "events (should be 0) until pre-beginning", r1
    r2 = x.until(day_3)
    print len(r2), "events (should be 2) until", day_3, r2
    r3 = x.until(day_after_all)
    print len(r3), "events (should be 4) until after-ending", r3
    r4 = x.since(day_before_all)
    print len(r4), "events (should be 4) since pre-beginning", r4
    r5 = x.since(day_3)
    print len(r5), "events (should be 2) since", day_3, r5
    r6 = x.since(day_after_all)
    print len(r6), "events (should be 0) since after-ending", r6
    r7 = x.between(day_before_all, day_3)
    print len(r7), "events (should be 2) between", day_before_all, "and", day_3, r7
    r8 = x.between(day_1, day_5)
    print len(r8), "events (should be 2) between", day_1, "and", day_5, r8
    r9 = x.between(day_3, day_after_all)
    print len(r9), "events (should be 2) between", day_3, "and", day_after_all, r9
    print "next meeting is", x.next(day_0, event_types=['meeting'])
    print "latest meeting is", x.latest(day_6, event_types=['meeting'])
    print "latest laser training is", x.latest(day_after_all,
                                               event_types=['training'],
                                               equipment='laser')
