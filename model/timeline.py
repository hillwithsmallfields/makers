from datetime import datetime
import database

class Timeline(object):

    def __init__(self):
        characteristics = {}
        events = []

    @staticmethod
    def create_timeline(**kwargs):
        TL = Timeline()
        TL.events = database.get_events(**kwargs)
        TL.characteristics = kwargs # so we can refresh the events list
        return TL

    def events(self):
        return self.events

    @staticmethod
    def future_events(**kwargs):
        """List the events which have not yet started."""
        return Timeline.create_timeline(earliest=datetime.now(),
                                        **kwargs)

    @staticmethod
    def present_events(**kwargs):
        """List the events which have started but not finished."""
        return Timeline.create_timeline(earliest=datetime.now(),
                                        latest=datetime.now(),
                                        **kwargs)

    @staticmethod
    def past_events(**kwargs):
        """List the events which have finished."""
        return Timeline.create_timeline(latest=datetime.now(),
                                        **kwargs)

    def refresh(self):
        self.events = database.get_events(**self.characteristics)
