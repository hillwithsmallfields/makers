#!/usr/bin/python

from nevow import tags as T
from nevow import flat
import configuration

def timeslots_form(config, values):
    """Make a timeslots form, with some values pre-checked."""
    times = config['timeslots']['times']
    slots = len(times)
    return T.table[T.tr[T.td[""],
                        [T.th[slot] for slot in slots]],
                   [T.tr[T.th[day]]
                            for day in config['timeslots']['days']]]

def test_timeslots():
    print flat.flatten(timeslots_form(config.get_config(), 12345))

if __name__ == "__main__":
    test_timeslots()
