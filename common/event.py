
import database
import re
from datetime import datetime, timedelta

fulltime = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}[T ][0-9]{2}:[0-9]{2}:[0-9]{2}")

def as_time(clue):
    return (clue
            if isinstance(clue, datetime)
            else (datetime.fromordinal(clue)
                  if isinstance(clue, int)
                  else (datetime.strptime(clue, "%Y-%m-%dT%H:%M:%S"
                                          if fulltime.match(clue)
                                          else "%Y-%m-%d")
                        if isinstance(clue, basestring)
                        else None)))


class Event(object):

    # keep a hash of events so each one is only in memory once
    events_by_id = {}

    def __init__(self, event_type,
                 event_datetime,
                 hosts,
                 attendees=[],
                 event_duration=60,
                 equipment=None):
        """Create an event of a given type and datetime.
        The current user is added as a host.
        The event type names a template to build the event from.
        An event template is an event which is copied.
        The event is not saved and scheduled yet."""
        # self.details = get_event_template(event_type)
        self.event_type = event_type
        self.start = as_time(event_datetime)
        self.duration = (event_duration
                         if isinstance(event_duration, timedelta)
                         else (timedelta(0, event_duration * 60) # given in minutes
                               if isinstance(event_duration, int)
                               else None))
        self.hosts = hosts
        self.attendees = attendees
        self.equipment = equipment # a list, not a single item
        self._id = None
        # 'hosts': [], # todo: put the current user in as a host
        # 'attendees': [],
        # # preconditions; not sure of the format of this
        # 'prerequisites': [],
        # # What the event will result in, if training
        # 'aim': None,      # what role the event trains for
        # 'equipment_classes': [],
        # # What the event needs to reserve
        # 'location': None,
        # 'equipment': []

    def __str__(self):
        accum = "<" + self.event_type
        accum += "_event at " + str(self.start) # todo: don't print time if it's all zeroes, just print date
        if self.hosts and self.hosts != []:
            accum += " with " + ",".join(map(str, self.hosts))
        if self.equipment and self.equipment != []:
            accum += " on " + ",".join(self.equipment)
        accum += ">"
        return accum

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def find(event_type, event_datetime, hosts, equipment):
        event_datetime = as_time(event_datetime)
        event_dict = database.get_event(event_type, event_datetime, hosts, equipment, create=True)
        if event_dict is None:
            return None
        event_id = event_dict['_id']
        if event_id not in Event.events_by_id:
            Event.events_by_id[event_id] = Event(event_type, event_datetime, hosts, equipment=equipment)
        e = Event.events_by_id[event_id]
        e.__dict__.update(event_dict)
        return e

    @staticmethod
    def find_by_id(event_id):
        event_dict = database.get_event_by_id(event_id)
        if event_dict is None:
            return None
        if event_id not in Event.events_by_id:
            Event.events_by_id[event_id] = Event(event_dict['event_type'],
                                                 event_dict['event_datetime'],
                                                 event_dict['hosts'],
                                                 equipment=event_dict['equipment'])
        e = Event.events_by_id[event_id]
        e.__dict__.update(event_dict) # todo: sort out whether I need to re-read this in case of database changes
        return e

    def get_details(self):
        """Get the details of an event, as a dictionary."""
        return self.__dict__

    def set_details(self, details_dict):
        """Set the details of an event, from a dictionary."""
        self.__dict__.update(details_dict)

    def schedule(self):
        """Save the event to the database, and add it to the list of scheduled events."""
        pass

    def cancel(self):
        """Remove the event to the list of scheduled events."""
        pass

    def get_hosts(self):
        """Return the list of people hosting the event."""
        pass

    def add_hosts(self, *hosts):
        """Add specified hosts to the hosts list."""
        pass

    def remove_hosts(self, *hosts):
        """Remove specified hosts from the hosts list."""
        pass

    def get_attendees(self):
        """Return the list of people attending the event."""
        pass

    def add_attendees(self, *attendees):
        """Add specified people to the attendees list."""
        pass

    def remove_attendees(self, *attendees):
        """Remove specified people from the attendees list."""
        pass

    def mark_results(self, *attendees):
        """Record the results of a training session."""
        pass

    def save_as_template(self, name):
        """Save this event as a named template."""
        pass

def get_event_template(name):
    """Find an event template by name."""
    # todo: there should be a collection of event templates in the database
    return None

def as_id(event):
    """Given an event or id, return the id."""
    return event._id if type(event) == Event else event

def as_event(event):
    """Given an event or id, return the event."""
    return event if type(event) == Event else Event.events_by_id.get(event, None)
