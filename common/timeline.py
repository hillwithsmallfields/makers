import datetime

class Timeline(object):

    def __init__(self):
        self.events = []             # in time order, latest first

    def __str__(self):
        return "[" + " ".join(map(str, self.events)) + "]"

    def __repr__(self):
        return self.__str__()

    def insert(self, event):
        """Insert an event at its place in the timeline."""
        pass

    def until(self, when):
        """Return all the events up to a given time."""
        pass

    def since(self, when):
        """Return all the events since a given time."""
        pass

    def between(self, begin, end):
        """Return all the events between two given times."""
        pass

    def next(self, when, event_types=None, locations=None):
        """Return the next event matching the given criteria."""
        if when is None:
            when = datetime.datetime.now()
        pass

    def latest(self, when, event_types=None, locations=None):
        """Return the latest event matching the given criteria."""
        if when is None:
            when = datetime.datetime.now()
        pass
