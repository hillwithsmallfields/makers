import database

class Person(object):

    def __init__(self):
        self.email = None
        self._id = None
        self.link_id = None
        self.surname = None
        self.given_name = None
        self.known_as = None
        self.membership_number = None
        self.fob = None
        self.events = []
        self.available = 0      # bitmap of timeslots, lowest bit is Monday morning, etc
        self.profile = {}       # bag of stuff like address
        pass

    def __str__(self):
        return ("<member " + str(self.membership_number)
                + " " + self.name()
                + ">")

    def __repr__(self):
        return "<member " + str(self.membership_number) + ">"

    @staticmethod
    def find(identification):
        """Find a person in the database."""
        data = database.get_person(identification)
        if data is None:
            return None
        # convert the dictionary into a Person object
        p = Person()
        p.__dict__.update(data)
        return p

    def name(self):
        """Return the person's name, unless they've requested anonymity."""
        # todo: add admin override of anonymity
        formal, _ = database.person_name(self.link_id)
        return formal.encode('utf-8')

    def nickname(self):
        """Return the person's nickname, unless they've requested anonymity."""
        # todo: add admin override of anonymity
        _, informal = database.person_name(self.link_id)
        return informal

    def set_profile_field(self, *kwargs):
        """Set the fields and write them back to the database."""
        pass

    def add_event(self, event):
        """Add the event to the appropriate role list of the person's events, and write it back to the database."""
        # note that the role can be found from 'aim' field of the event details,
        # and the equipment classes from the 'equipment_classes' of the event details
        # training event lists are kept in time order, with the latest (which may be in the future) at the front of the list
        database.database[database.collection_names['people']].update({"_id" : self._id},
                                                                      # todo: this seems to be replacing the front event, not prepending (but is it a list already?)
                                                                       {'$set': {'events.-1': event}})

    def get_equipment_classes(self, role):
        """Get the list of the equipment_classes for which the person has the specified role."""
        pass

    def is_qualified(self, equipment_class, role):
        """Return whether the user is qualified for a role on an equipment class."""
        for transition in self.role_transitions[role]:
            details = transition.get_details()
            if equipment_class not in details['equipment_classes']:
                continue
        # todo: throw away any future events in transitions
        pass

    def is_member(self):
        """Return whether the person is a member."""
        return is_trained(self, configuration.get_config()['organization']['name'])

    def is_administrator(self):
        """Return whether the person is an admin."""
        return self.is_owner(get_config()['organization']['database'])

    def is_auditor(self):
        """Return whether the person is an auditor.
        Similar to admin but read-only."""
        return self.is_trained(get_config()['organization']['database'])

    def is_inductor(self):
        """Return whether the person is a general inductor."""
        return self.is_trainer(configuration.get_config()['organization']['name'])

    def is_trained(self, equipment_class):
        """Return whether a person is trained to use a particular equipment_class."""
        return self.is_qualified(equipment_class, 'user')

    def is_owner(self, equipment_class):
        """Return whether the person is an owner of that equipment_class."""
        return self.is_qualified(equipment_class, 'owner')

    def is_trainer(self, equipment_class):
        """Return whether the person is a trainer for that equipment_class."""
        return self.is_qualified(equipment_class, 'trainer')

def all_people():
    """Return a list of all registered people."""
    return [ person for person in people_collection.find({}) ]

def all_members():
    """Return a list of all current members."""
    return [ person for person in people_collection.find({})
             if person.is_member()]
