import database

class Equipment_type(object):

    types_by_id = {}
    types_by_name = {}

    def __init__(self):
        """Set up an equipment type structure."""
        self.name = None
        self.training_category = None
        self.manufacturer = None

    def __str__(self):
        return "<type " + self.name + " (" + self.training_category + ")>"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def find(name):
        if name in Equipment_type.types_by_name:
            return Equipment_type.types_by_name[name]
        data = database.get_equipment_type_dict(name)
        if data is None:
            return None
        c = Equipment_type()
        c.__dict__.update(data)
        Equipment_type.types_by_id[data['_id']] = c
        Equipment_type.types_by_name[data['name']] = c
        return c

    def get_machines(self):
        """List the individual machines of an equipment type."""
        # todo: search the equipment collection
        pass

    def get_people(self, role):
        """Return the trained users, owners, or trainers of an equipment type."""
        # todo: search the people collection for those who have attended the appropriate qualifying events
        pass

    def get_trained_users(self):
        """Return a list of the people allowed to use the equipment type."""
        return self.get_people('trained')

    def get_owners(self):
        """Return a list of the owners of the equipment type."""
        return self.get_people('owners')

    def get_trainers(self):
        """Return a list of the people who can train others to use the equipment type.
        If no trainers are defined, the owners are the trainers."""
        trainers = self.get_people('trainers')
        if trainers is None or len(trainers) == 0:
            trainers = self.get_owners()
        return trainers

    def request_training(self, person):
        """Note that a person has requested training on this equipment type.
        The data is actually stored with the person's record, not the
        equipment type record, so this is just a secondary
        presentation of the action."""
        pass
