import database

class Person(object):

    def __init__(self, identification):
        """Find a person in the database."""
        # todo: fetch the person entry from the database
        # self.role_transitions = {'user': [],
        #               'owner': [],
        #               'trainer': []}
        pass

    @staticmethod
    def get(identification):
        return database.get_person(identification)

    def set_profile_field(self, *kwargs):
        """Set the fields and write them back to the database."""
        pass

    def add_training(self, event):
        """Add the event to the appropriate role list of the person's training, and write it back to the database."""
        # note that the role can be found from 'aim' field of the event details,
        # and the equipment classes from the 'equipment_classes' of the event details
        # training event lists are kept in time order, with the latest (which may be in the future) at the front of the list
        pass

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
