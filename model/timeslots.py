#!/usr/bin/python

# Represent availability in a week, within a 32-bit integer.

# Each four bits represents one day's time slots (morning, afternoon,
# evening, optinally other).

# When an event is scheduled, it's then easy to search for who may be
# able to make that time.

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
