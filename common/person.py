import database
import timeline
# from event import Event
import event
import configuration
import equipment_type
from datetime import datetime

class Person(object):

    people_by_id = {}

    def __init__(self):
        self.email = None
        self._id = None
        self.link_id = None
        self.surname = None
        self.given_name = None
        self.known_as = None
        self.membership_number = None
        self.fob = None
        self.training = None
        self.available = 0      # bitmap of timeslots, lowest bit is Monday morning, etc
        self.profile = {}       # bag of stuff like address

    def __str__(self):
        return ("<member " + str(self.membership_number)
                + " " + self.name()
                + ">")

    def __repr__(self):
        return "<member " + str(self.membership_number) + ">"

    @staticmethod
    def find(identification):
        """Find a person in the database."""
        data = identification if type(identification) is dict else database.get_person_dict(identification)
        if data is None:
            return None
        # convert the dictionary into a Person object
        person_id = data['_id']
        if person_id not in Person.people_by_id:
            Person.people_by_id[person_id] = Person()
        p = Person.people_by_id[person_id]
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
        return informal.encode('utf-8')

    def set_profile_field(self, *kwargs):
        """Set the fields and write them back to the database."""
        pass

    def get_training_timeline(self):
        """Return the training data for this user,
        as a timeline of training events.
        What is stored in the user record is just the _id of the timeline,
        because timelines are stored as records in their own right."""
        # todo: stop storing the timeline as such, and generate it by searching the database
        # return timeline.Timeline.find_by_id(self.training)
        pass

    def get_training_events(self, event_type='user_training', when=None):
        """Return the training data for this user,
        as a list of training events."""
        # todo: handle the when parameter
        return database.get_events(event_type=event_type,
                                   person_field='passed',
                                   person_id=self._id,
        )

    def add_training(self, event):
        """Add the event to the appropriate role list of the person's events, and write it back to the database."""
        # note that the role can be found from 'aim' field of the event details,
        # and the equipment classes from the 'equipment_classes' of the event details
        # training event lists are kept in time order, with the latest (which may be in the future) at the front of the list
        # if self.training is None:
        #     self.training = timeline.Timeline(self.given_name + " " + self.surname + "'s training")._id
        #     database.database[database.collection_names['people']].update({'_id': self._id}, {'$set': {'training': self.training}})
        # self.get_training_timeline().insert(event)
        pass

    def get_equipment_classes(self, role, when=None):
        """Get the list of the equipment_classes for which the person has the specified role."""
        role_training = role + "_training"
        role_untraining = role + "_untraining"
        training = self.get_training_events(event_type = role_training, when=when or datetime.now())
        untraining = self.get_training_events(event_type = role_untraining, when=when or datetime.now())
        trained = {}
        detrained = {}
        equipments = {}
        for ev in training:
            for eq in ev.equipment:
                trained[eq] = ev.start
                equipments[eq] = eq
        for ev in untraining:
            for eq in ev.equipment:
                detrained[eq] = ev.start
        return [ equipment_type.Equipment_type.find_by_id(equipments[e])
                 for e in trained.keys()
                 if (e not in detrained
                     or trained[e] > detrained[e])]

    def qualification(self, equipment_type, role, when=None):
        """Return whether the user is qualified for a role on an equipment class.
        The result is the event that qualified them."""
        role_training = role + "_training"
        role_untraining = role + "_untraining"
        for event in self.get_training_events(when or datetime.now()):
            if equipment_type not in event.equipment:
                continue
            if event.event_type == role_training:
                if self._id in event.passed:
                    return event
            if event.event_type == role_untraining:
                return None
        return None

    def is_member(self):
        """Return whether the person is a member."""
        return self.qualification(configuration.get_config()['organization']['name'], 'user')

    def is_administrator(self):
        """Return whether the person is an admin."""
        return self.is_owner(configuration.get_config()['organization']['database'])

    def is_auditor(self):
        """Return whether the person is an auditor.
        Similar to admin but read-only."""
        return self.is_trained(configuration.get_config()['organization']['database'])

    def is_inductor(self):
        """Return whether the person is a general inductor."""
        return self.is_trainer(configuration.get_config()['organization']['name'])

    def is_trained(self, equipment_class):
        """Return whether a person is trained to use a particular equipment_class."""
        return self.qualification(equipment_class, 'user')

    def is_owner(self, equipment_class):
        """Return whether the person is an owner of that equipment_class."""
        return self.qualification(equipment_class, 'owner')

    def is_trainer(self, equipment_class):
        """Return whether the person is a trainer for that equipment_class."""
        return self.qualification(equipment_class, 'trainer')

def all_people():
    """Return a list of all registered people."""
    return [ Person.find(person) for person in database.database[database.collection_names['people']].find({}) ]

def all_members():
    """Return a list of all current members."""
    return [ person for person in database.database[database.collection_names['people']].find({})
             if person.is_member()]
