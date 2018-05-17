import database

class Timeline (object):

    def __init__(self):
        characteristics = {}
        events = []

    @staticmethod
    def create_timeline(**kwargs):
        TL = Timeline()
        TL.events = database.get_events(**kwargs)
        TL.characteristics = kwargs
        return TL

    def events(self):
        return self.events

    def update(self):
        self.events = database.get_events(**self.characteristics)
