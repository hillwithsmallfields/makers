
from nevow import tags as T
from nevow import flat

def timeslots_form(config, values):
    """Make a timeslots form, with some values pre-checked."""
    times = config['timeslots']['times']
    slots = len(times)
    return T.table[T.tr[T.td[""],
                        [T.th[slot] for slot in slots]],
                   [T.tr[T.th[day]]
                            for day in config['timeslots']['days']]]
