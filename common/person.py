import database

class Person(object):

    def __init__(self, identification):
        """Find a person in the database."""
        pass

    def set_profile_field(self, *kwargs):
        """Set the fields and write them back to the database."""
        pass

    def add_training(self, event):
        """Add the event to the appropriate role list of the person's training, and write it back to the database."""
        # note that the role can be found from the event
        pass

    def get_machines(self, role):
        """Get the list of the machines for which the person has the specified role."""
        pass

    def is_member(self):
        """Return whether the person is a member."""
        pass

    def is_administrator(self):
        """Return whether the person is an admin."""
        pass

    def is_inductor(self):
        """Return whether the person is a general inductor."""
        pass

    def is_trained(self, machine):
        """Return whether a person is trained to use a particular machine."""
        pass

    def is_owner(self, machine):
        """Return whether the person is an owner of that machine."""
        pass

    def is_trained(self, machine):
        """Return whether the person is a trainer for that machine."""
        pass

def all_people():
    """Return a list of all registered people."""
    return [ person for person in people_collection.find({}) ]

def all_members():
    """Return a list of all current members."""
    return [ person for person in people_collection.find({})
             if person.is_member()]

def add_person(record):
    print "Adding person", record, "to collection", people_collection
    # todo: convert dates to datetime.datetime
    # todo: possibly use upsert
    database.people_collection.insert(record)
