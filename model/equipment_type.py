import datetime
import model.database
import model.machine
import model.pages
import model.person

def id_to_name(as_id):
    # return model.person.Person.find(as_id).name()
    try:
        return person.Person.find(as_id).name()
    except:
        try:
            return person.Person.find(as_id)
        except:
            return "id" + str(as_id)

class Equipment_type(object):

    """An Equipment_type is the unit of what people can be trained on.

    The normal way to get an Equipment_type object is through the
    class methods 'find' (which takes a name) and 'find_by_id', which
    takes a mongodb ObjectId.

    """

    types_by_id = {}
    types_by_name = {}

    def __init__(self):
        """Set up an equipment type structure."""
        self.name = None
        self.presentation_name = None
        self.training_category = None
        self.manufacturer = None
        self.description = None
        self.picture = None
        self._id = None

    def __str__(self):
        return "<equipment_type " + self.name + " (" + self.training_category + ")>"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def find(name):
        if isinstance(name, Equipment_type):
            return name
        name = model.pages.unstring_id(name)
        if name in Equipment_type.types_by_name:
            return Equipment_type.types_by_name[name]
        data = model.database.get_equipment_type_dict(name)
        if data is None:
            return None
        c = Equipment_type()
        c.__dict__.update(data)
        Equipment_type.types_by_id[data['_id']] = c
        Equipment_type.types_by_name[data['name']] = c
        return c

    @staticmethod
    def find_by_id(this_id):
        this_id = model.pages.unstring_id(this_id)
        if this_id in Equipment_type.types_by_id:
            return Equipment_type.types_by_id[this_id]
        data = model.database.get_equipment_type_dict(this_id)
        if data is None:
            return None
        c = Equipment_type()
        c.__dict__.update(data)
        Equipment_type.types_by_id[data['_id']] = c
        Equipment_type.types_by_name[data['name']] = c
        return c

    @staticmethod
    def list_equipment_types(training_category=None):
        return [ Equipment_type.find_by_id(et_dict['_id'])
                 for et_dict in model.database.list_equipment_types(training_category) ]

    @staticmethod
    def API_all_equipment_fobs():
        pairs = [ (eqt.name, eqt.API_enabled_fobs()) for eqt in Equipment_type.list_equipment_types() ]
        return { name: fobs for (name,fobs) in pairs if len(fobs) > 0 }

    def pretty_name(self):
        """Return the presentation version of the name of the type."""
        return self.presentation_name or self.name.replace('_', ' ').capitalize()

    def get_machines(self):
        """List the individual machines of an equipment type."""
        return [ model.machine.Machine.find_by_id(mc['_id']) for mc in model.database.get_machine_dicts_for_type(self._id) ]

    def get_people_events(self, role):
        """Return the events indicating the training users, owners, or trainers of an equipment type."""
        now = datetime.datetime.now()
        training = model.database.get_eqtype_events(self._id,
                                                    model.database.role_training(role),
                                                    latest=now)
        untraining = model.database.get_eqtype_events(self._id,
                                                      model.database.role_untraining(role),
                                                      latest=now)
        trained = {}
        detrained = {}
        # working our way back in time, we want only the most recent relevant event of each type
        for ev in training:
            for trained_person in ev.passed:
                if trained_person not in trained:
                    trained[trained_person] = ev
        for ev in untraining:
            for detrained_person in ev.passed:
                if detrained_person not in detrained:
                    detrained[detrained_person] = ev
        # print("people trained on", self.name, "are", trained)
        # print("people detrained on", self.name, "are", detrained)
        return trained, detrained

    def get_people(self, role):
        """Return the trained users, owners, or trainers of an equipment type."""
        trained, detrained = self.get_people_events(role)
        return [ model.person.Person.find(trained_person) for trained_person in trained.keys()
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

    def backup_API_people(self, role):
        """Return a list of dictionaries describing who has a given role on this equipment type.
        The result can be given to a csv.DictWriter to produce a file in the same format from
        which the user data was originally imported.  In case of losing the database, a set of these
        files can be used to reconstruct the most important data in it.
        The "role" argument can be 'user', 'owner', or 'trainer'."""
        trained, detrained = self.get_people_events(role)
        as_list = [ {'Name': id_to_name(trained_person_id),
                     'Equipment': self.name,
                     'Trainer': id_to_name(trained[trained_person_id].hosts[0]),
                     'Date': model.times.timestring(trained[trained_person_id].start)}
                    for trained_person_id in trained.keys()
                    if (trained_person_id not in detrained
                        or trained[trained_person_id].start > detrained[trained_person_id].start) ]
        # as_list = sorted(as_list, key=lambda whoever: whoever['name'])
        return as_list

    def API_enabled_fobs(self):
        return [ user.fob for user in self.get_trained_users() ]

    def request_training(self, whoever):
        """Note that a person has requested training on this equipment type.
        The data is actually stored with the person's record, not the
        equipment type record, so this is just a secondary
        presentation of the action."""
        whoever.add_training_request(role, self)

    def cancel_training_request(self, whoever):
        """Note that a person has cancelled their request for training on this equipment type.
        The data is actually stored with the person's record, not the
        equipment type record, so this is just a secondary
        presentation of the action."""
        whoever.remove_training_request(role, [self])

    def get_training_requests(self, role='user'):
        """Return a dictionary of people ids to lists of training requests.
        There should normally be only one entry in the list.
        The training request is in the form of a dictionary as constructed by person.Person.add_training_request."""
        return {y._id: [z for z in y.training_requests
                        if self._id == z['equipment_type']]
                 for y in [model.person.Person.find(x)
                            for x in model.database.get_people_awaiting_training(model.database.role_training(role), [self._id])]}

    def get_training_events(self, role, earliest=None, latest=None):
        """Return a list of training events for this type of equipment."""
        return model.database.get_eqtype_events(self._id, model.database.role_training(role), earliest, latest)
