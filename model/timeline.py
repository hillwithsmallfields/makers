from datetime import datetime
import model.database

class Timeline(object):

    """A Timeline holds a sequence of timed events.

    Its class methods allow you to collect up past, present or future events that match some given criteria.

    The criteria can include:

    - event_type

    - person_field and person_id (together) where person_field can be
      'hosts', 'attendee', 'passed', 'failed', or 'noshow'.

    - include_hidden to include unpublished events

    """

    def __init__(self):
        characteristics = {}
        events = []

    @staticmethod
    def create_timeline(**kwargs):
        TL = Timeline()
        TL.events = model.database.get_events(**kwargs)
        TL.characteristics = kwargs # so we can refresh the events list
        return TL

    def events(self):
        return self.events

    @staticmethod
    def future_events(**kwargs):
        """List the events which have not yet started.

        See the class documentation for the available search criteria."""
        return Timeline.create_timeline(earliest=datetime.now(),
                                        **kwargs)

    @staticmethod
    def present_events(**kwargs):
        """List the events which have started but not finished.

        See the class documentation for the available search criteria."""
        return Timeline.create_timeline(earliest=datetime.now(),
                                        latest=datetime.now(),
                                        **kwargs)

    @staticmethod
    def past_events(**kwargs):
        """List the events which have finished.

        See the class documentation for the available search criteria."""
        return Timeline.create_timeline(latest=datetime.now(),
                                        **kwargs)

    def refresh(self):
        """Update the list of events in this timeline.

        The original criteria are used."""
        self.events = model.database.get_events(**self.characteristics)
