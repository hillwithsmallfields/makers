#!/usr/bin/python

# Represent availability in a week, within a 32-bit integer.

# Each four bits represents one day's time slots (morning, afternoon,
# evening, optinally other).

# When an event is scheduled, it's then easy to search for who may be
# able to make that time.

import configuration
import datetime

def _timeslots_dayparts_to_int(day):
    return (0 if len(day) == 0
            else ((1 if day[0] else 0)
                  | (_timeslots_dayparts_to_int(day[1:]) << 1)))

def timeslots_to_int(timeslots):
    """Convert a list of lists of available times, to a number.
    Each sub-list represents four timeslots for one day.
    The lowest bit of the number is the first timeslot of the first day."""
    return (0 if len (timeslots) == 0
            else (_timeslots_dayparts_to_int(timeslots[0])
                  | (timeslots_to_int(timeslots[1:]) << 4)))

def _timeslots_from_dayparts_number(number):
    return [ (number & (1 << i)) != 0
             for i in range(0,4) ]

def timeslots_from_int(number):
    """Convert a number to a list of lists of available times.
    Each sub-list represents four timeslots for one day.
    The lowest bit of the number is the first timeslot of the first day."""
    return [ _timeslots_from_dayparts_number(number >> (b*4))
             for b in range(0,7) ]

day_order = None
periods = None
period_order = None

def get_slots_conf():
    global day_order, periods, period_order
    slotconf = configuration.get_config()['timeslots']
    if day_order is None:
        day_order = slotconf['days']
    if periods is None:
        periods = { pname: [ pval for pval in
                             map(lambda pair: datetime.time(pair[0], pair[1]),
                               [ [ int(x) for x in slot.strip().split(':') ]
                                 for slot in pdescr.split('--') ]) ]
                    for pname, pdescr in slotconf['periods'].items() }
    if period_order is None:
        tmp = { startend[0]: name for name, startend in periods.items() }
        period_order = [ tmp[tm] for tm in sorted(tmp.keys()) ] + ['other']
    return day_order, periods, period_order

def time_to_timeslot(when):
    """Convert a datetime to a timeslots bitmap."""
    days, times, order = get_slots_conf()
    timeofday = when.time()
    timename = 'other'
    for pname, ppair in times.items():
        if timeofday >= ppair[0] and timeofday <= ppair[1]:
            timename = pname
    time_slot_number = order.index(timename)
    # print "timename", timename, "time_slot_number", time_slot_number
    return 1 << (time_slot_number + when.weekday() * 4)
