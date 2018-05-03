# -*- coding: utf8
import database
from equipment_type import Equipment_type
import re
from datetime import datetime, timedelta
import person

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
                 equipment_types=[],
                 equipment=[]):
        """Create an event of a given type and datetime.
        The current user is added as a host.
        The event type names a template to build the event from.
        An event template is an event which is copied.
        The event is not saved and scheduled yet."""
        # self.details = get_event_template(event_type)
        self.event_type = event_type
        self.start = as_time(event_datetime)
        self.end = self.start + (event_duration
                                 if isinstance(event_duration, timedelta)
                                 else (timedelta(0, event_duration * 60) # given in minutes
                                       if isinstance(event_duration, int)
                                       else timedelta(0, 120 * 60)))
        # It would be nice to use Python sets for these,
        # but then we'd have to convert them for loading and saving in mongo.
        self.hosts = hosts         # _id of person
        self.attendees = attendees # _id of person
        self.equipment_types = equipment_types
        self.equipment = equipment
        self._id = None
        self.passed = []   # _id of person
        self.failed = []   # _id of person
        self.noshow = []   # _id of person
        self.prerequisites = []
        self.location = None
        # 'prerequisites': [],
        # # What the event will result in, if training
        # 'aim': None,      # what role the event trains for
        # 'equipment_classes': [],
        # # What the event needs to reserve

    def __str__(self):
        accum = "<" + self.event_type
        accum += "_event at " + str(self.start) # todo: don't print time if it's all zeroes, just print date
        if self.hosts and self.hosts != []:
            accum += " with " + ",".join([person.Person.find(host_id).name()
                                          for host_id in self.hosts]).encode('utf-8')
        if self.equipment and self.equipment != []:
            accum += " on " + ",".join([Equipment_type.find(e).name for e in self.equipment])
        accum += ">"
        return accum

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def find(event_type, event_datetime, hosts, equipment_types):
        event_datetime = as_time(event_datetime)
        event_dict = database.get_event(event_type, event_datetime,
                                        hosts,
                                        equipment_types,
                                        create=True)
        if event_dict is None:
            return None
        event_id = event_dict['_id']
        if event_id not in Event.events_by_id:
            Event.events_by_id[event_id] = Event(event_type, event_datetime,
                                                 hosts,
                                                 equipment_types=equipment_types)
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
                                                 equipment_types=event_dict['equipment_types'])
        e = Event.events_by_id[event_id]
        e.__dict__.update(event_dict) # todo: sort out whether I need to re-read this in case of database changes
        return e

    def get_details(self):
        """Get the details of an event, as a dictionary."""
        return self.__dict__

    def set_details(self, details_dict):
        """Set the details of an event, from a dictionary."""
        self.__dict__.update(details_dict)

    def save(self):
        """Save the event to the database."""
        database.save_event(self.__dict__)

    def schedule(self):
        """Save the event to the database, and add it to the list of scheduled events."""
        pass

    def cancel(self):
        """Remove the event to the list of scheduled events."""
        pass

    def get_hosts(self):
        """Return the list of people hosting the event."""
        return self.hosts

    def add_hosts(self, hosts):
        """Add specified hosts to the hosts list."""
        for host in hosts:
            if host not in self.hosts:
                self.hosts.append(host._id)
        self.save()

    def remove_hosts(self, hosts):
        """Remove specified hosts from the hosts list."""
        for host in hosts:
            if host in self.hosts:
                self.hosts.remove(host._id)
        self.save()

    def get_attendees(self):
        """Return the list of people attending the event."""
        return self.attendees

    def add_attendees(self, attendees):
        """Add specified people to the attendees list."""
        for attendee in attendees:
            if attendee not in self.attendees:
                self.attendees.append(attendee._id)
        self.save()

    def remove_attendees(self, attendees):
        """Remove specified people from the attendees list."""
        for attendee in attendees:
            if attendee in self.attendees:
                self.attendees.remove(attendee._id)
        self.save()

    def mark_results(self, successful, failed, noshow):
        """Record the results of a training session."""
        for whoever in successful:
            if whoever not in self.passed:
                self.passed.append(whoever._id)
        for whoever in failed:
            if whoever not in self.failed:
                self.failed.append(whoever._id)
        for whoever in noshow:
            if whoever not in self.noshow:
                self.noshow.append(whoever._id)
        self.save()

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
