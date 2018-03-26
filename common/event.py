
class Event(object):

    def __init__(self, event_type, event_datetime):
        """Create an event of a given type and datetime.
        The current user is added as a host."""
        pass

    def get_details(self):
        """Get the details of an event, as a dictionary."""
        pass

    def set_details(self, details_dict):
        """Set the details of an event, from a dictionary."""
        pass

    def schedule(self):
        """Add the event to the list of scheduled events."""
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
