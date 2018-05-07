import database
import person

class Equipment_type(object):

    types_by_id = {}
    types_by_name = {}

    def __init__(self):
        """Set up an equipment type structure."""
        self.name = None
        self.training_category = None
        self.manufacturer = None
        self._id = None

    def __str__(self):
        return "<equipment_type " + self.name + " (" + self.training_category + ")>"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def find(name):
        if isinstance(name, Equipment_type):
            return name
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

    @staticmethod
    def find_by_id(id):
        if id in Equipment_type.types_by_id:
            return Equipment_type.types_by_id[id]
        data = database.get_equipment_type_dict(id)
        if data is None:
            return None
        c = Equipment_type()
        c.__dict__.update(data)
        Equipment_type.types_by_id[data['_id']] = c
        Equipment_type.types_by_name[data['name']] = c
        return c

    @staticmethod
    def list_equipment_types():
        return [ Equipment_type.find_by_id(et_dict['_id'])
                 for et_dict in database.list_equipment_types() ]

    @staticmethod
    def API_all_equipment_fobs():
        return { eqt.name: eqt.API_enabled_fobs() for eqt in Equipment_type.list_equipment_types() }

    def get_machines(self):
        """List the individual machines of an equipment type."""
        # todo: search the equipment collection
        pass

    def get_people(self, role):
        """Return the trained users, owners, or trainers of an equipment type."""
        training = database.get_eqtype_events(self._id, database.role_training(role))
        untraining = database.get_eqtype_events(self._id, database.role_untraining(role))
        trained = {}
        detrained = {}
        # working our way back in time, we want only the most recent relevant event of eavh type
        for ev in training:
            for trained_person in ev.passed:
                if trained_person not in trained:
                    trained[trained_person] = ev
        for ev in untraining:
            for detrained_person in ev.passed:
                if detrained_person not in detrained:
                    detrained[detrained_person] = ev
        return [ person.Person.find(trained_person) for trained_person in trained.keys()
                 if (trained_person not in detrained
                     or trained[trained_person].start > detrained[trained_person].start) ]

    def get_trained_users(self):
        """Return a list of the people allowed to use the equipment type."""
        return self.get_people('user')

    def get_owners(self):
        """Return a list of the owners of the equipment type."""
        return self.get_people('owner')

    def get_trainers(self):
        """Return a list of the people who can train others to use the equipment type.
        If no trainers are defined, the owners are the trainers."""
        trainers = self.get_people('trainer')
        if trainers is None or len(trainers) == 0:
            trainers = self.get_owners()
        return trainers

    def API_enabled_fobs(self):
        return [ user.fob for user in self.get_trained_users() ]

    def request_training(self, person):
        """Note that a person has requested training on this equipment type.
        The data is actually stored with the person's record, not the
        equipment type record, so this is just a secondary
        presentation of the action."""
        pass
