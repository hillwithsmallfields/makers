
class Event(object):

    def __init__(self, event_type,
                 event_datetime, event_duration):
        """Create an event of a given type and datetime.
        The current user is added as a host.
        The event type names a template to build the event from.
        An event template is an event which is copied.
        The event is not saved and scheduled yet."""
        self.details = get_event_template(event_type)
        self.details['start'] = event_datetime,
        self.details['duration'] = event_duration
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
        pass

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
