
import database

class Event(object):

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
        self.details = get_event_template(event_type)
        self.start = event_datetime,
        self.event_type = event_type
        self.hosts = hosts
        self.attendees = attendees
        self.duration = event_duration
        self.equipment = equipment
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
        accum = "<" + self.event_type + "event at " + self.start
        if self.equipment and self.equipment != []:
            accum += " on " + ",".join(self.equipment)
        accum += ">"
        return accum

    def __repr__(self):
        return __str__(self)

    @staticmethod
    def find(event_type, event_datetime, hosts, equipment):
        event_dict = database.get_event(hosts, event_datetime, event_type, equipment, create=True)
        if event_dict is None:
            return None
        e = Event(event_type, event_datetime, hosts, equipment=equipment)
        e.__dict__.update(event_dict)
        return e

    def get_details(self):
        """Get the details of an event, as a dictionary."""
        pass

    def set_details(self, details_dict):
        """Set the details of an event, from a dictionary."""
        pass

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
