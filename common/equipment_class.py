
class Equipment_class(0bject):

    def __init__(self, identification):
        """Set up an equipment class structure from its name or other identification."""
        pass

    def get_machines(self):
        """List the individual machines of an equipment class."""
        # todo: search the equipment collection
        pass

    def get_people(self, role):
        """Return the trained users, owners, or trainers of an equipment class."""
        # todo: search the people collection for those who have attended the appropriate qualifying events
        pass

    def get_trained_users(self):
        """Return a list of the people allowed to use the equipment class."""
        return self.get_people('trained')

    def get_owners(self):
        """Return a list of the owners of the equipment class."""
        return self.get_people('owners')

    def get_trainers(self):
        """Return a list of the people who can train others to use the equipment class.
        If no trainers are defined, the owners are the trainers."""
        trainers = self.get_people('trainers')
        if trainers is None or len(trainers) == 0:
            trainers = self.get_owners()
        return trainers

    def request_training(self, person):
        """Note that a person has requested training on this equipment class.
        The data is actually stored with the person's record, not the
        equipment class record, so this is just a secondary
        presentation of the action."""
        pass
