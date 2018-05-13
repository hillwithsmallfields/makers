import database
import timeline
# from event import Event
import event
import configuration
import equipment_type
from datetime import datetime

# todo: induction input from jotform.com
# todo: suppress equipment access for non-members
# todo: admin to change training request dates


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
        self.requests = []      # list of dict with 'request_date', 'equipment_types' (as _id), 'event_type'
        self.training_requests_limit = None # normally comes from config but admins can override using this
        self.noshow_absolutions = 0
        self.available = 0xffffffff # bitmap of timeslots, lowest bit is Monday morning, etc
        self.profile = {}       # bag of stuff like address

    def __str__(self):
        return ("<member " + str(self.membership_number)
                + " " + self.name()
                + ">")

    def __repr__(self):
        return "<member " + str(self.membership_number) + ">"

    @staticmethod
    def list_all_people():
        return [ Person.find(whoever) for whoever in database.get_all_person_dicts() ]

    @staticmethod
    def list_all_members():
        return equipment_type.Equipment_type.find(configuration.get_config()['organization']['name']).get_trained_users()

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

    def save(self):
        """Save the person to the database."""
        database.save_person(self.__dict__)

    def set_fob(self, newfob):
        self.fob = newfob
        self.save()

    def set_profile_field(self, *kwargs):
        """Set the fields and write them back to the database."""
        pass

    def get_training_requests_limit(self):
        return (self.training_requests_limit
                or int(configuration.get_config()['training']['default_max_requests']))

    def set_training_requests_limit(self, limit):
        self.training_requests_limit = limit

    def absolve_noshows(self):
        self.noshow_absolutions = (len(self.get_training_events('yser_training', result='noshow'))
                                   + len(self.get_training_events('owner_training', result='noshow'))
                                   + len(self.get_training_events('trainer_training', result='noshow')))

    def add_training_request(self, role, equipment_types, when=None):
        """Register a a training request for one or more equipment types.
        The time should not normally be specified, as that would allow
        queue-jumping, although an admin might do that if someone convinces
        them that they have a reasonable need for urgent training.
        The role may be 'user','trainer', or 'owner'."""
        if len(self.get_training_requests()) > self.get_training_requests_limit():
            return False, "Too many open training requests"
        role_training = database.role_training(role)
        if ((len(self.get_training_events(role_training, result='noshow')) - self.noshow_absolutions)
            >= int(configuration.get_config()['training']['no_shows_limit'])):
            return False, "Too many no-shows"
        self.requests.append({'request_date': when or datetime.now(),
                              'equipment_types': [ equipment_type.Equipment_type.find(eqt)._id for eqt in equipment_types],
                              'event_type': role_training})
        self.save()
        return True, None

    def get_training_requests(self):
        keyed = { req['request_date']: req for req in self.requests }
        return [ keyed[d] for d in sorted(keyed.keys()) ]

    def get_training_timeline(self):
        """Return the training data for this user,
        as a timeline of training events.
        What is stored in the user record is just the _id of the timeline,
        because timelines are stored as records in their own right."""
        # todo: stop storing the timeline as such, and generate it by searching the database
        # return timeline.Timeline.find_by_id(self.training)
        pass

    def get_training_events(self, event_type='user_training', when=None,  result='passed'):
        """Return the training data for this user,
        as a list of training events."""
        # todo: handle the when parameter
        return database.get_events(event_type=event_type,
                                   person_field=result,
                                   person_id=self._id,
                                   include_hidden=True
                                   # ,as_recently_as=when
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

    @staticmethod
    def awaiting_training(event_type, equipment_types):
        """List the people who have requested a particular type of training."""
        return database.get_people_awaiting_training(event_type, equipment_types)

    def get_equipment_classes(self, role, when=None):
        """Get the list of the equipment_classes for which the person has the specified role."""
        # todo: pass the when parameter on
        trained = {}
        detrained = {}
        equipments = {}
        for ev in self.get_training_events(event_type = database.role_training(role),
                                           when=when or datetime.now()):
            for eq in ev.equipment:
                trained[eq] = ev.start
                equipments[eq] = eq
        for ev in self.get_training_events(event_type = database.role_untraining(role),
                                           when=when or datetime.now()):
            for eq in ev.equipment:
                detrained[eq] = ev.start
        return [ equipment_type.Equipment_type.find_by_id(equipments[e])
                 for e in trained.keys()
                 if (e not in detrained
                     or trained[e] > detrained[e])]

    def get_equipment_class_names(self, role):
        """Get the list of equipment types for which the user has a given role.
        Aimed mostly at the JSON API."""
        return [ eq.name for eq in self.get_equipment_classes(role) ]

    def get_qualifications(self, detailed=False):
        # aimed at JSON API
        quals = {}
        for role in ['user', 'owner', 'trainer']:
            q = self.get_equipment_class_names(role)
            if q:
                quals[role] = quals.get(role, []) + q
        return quals

    def qualification(self, equipment_type_name, role, when=None):
        """Return whether the user is qualified for a role on an equipment class.
        The result is the event that qualified them."""
        trained = None
        detrained = None
        equipment_id = equipment_type.Equipment_type.find(equipment_type_name)._id
        # print "qualification on", equipment_type_name, "role", role, "for", self.name(), "?"
        for ev in self.get_training_events(event_type = database.role_training(role),
                                           when=when or datetime.now()):
            # print "  is", equipment_id, "in", ev.equipment, "?"
            if equipment_id in ev.equipment:
                trained = ev
                break
        for ev in self.get_training_events(event_type = database.role_untraining(role),
                                           when=when or datetime.now()):
            if equipment_id in ev.equipment:
                detrained = ev.start
                break
        if detrained is None:
            # print "not detrained, returning", trained
            return trained
        if trained is None or detrained.start > trained.start:
            return None
        return trained

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

    def satisfies_condition(self, condition):
        equiptype, role = condition.split(' ')
        # print "satisfies_condition eq", equiptype, "role", role, "?"
        return self.qualification(equiptype, role)

    def satisfies_conditions(self, conditions):
        for condition in conditions:
            if not self.satisfies_condition(condition):
                return False
        return True

    def has_requested_training(self, equipment_types, role):
        # todo: I've seen it fail to show that someone has requested a training
        event_type = database.role_training(role)
        for req in self.requests:
            if req['event_type'] != event_type:
                continue
                for eqty in req['equipment_types']:
                    if eqty in equipment_types:
                        return req
        return None

    def api_personal_data(self, detailed=False):
        """Get the data for a user, in a suitable form for the API.
        With an optional flag, get more detail."""
        name, known_as = database.person_name(self)
        personal_data = {'name': name,
                         'qualified': self.get_qualifications()}
        # todo: add date joined
        if known_as:
            personal_data['known_as'] = known_as
        if self.membership_number:
            personal_data['membership_number'] = int(self.membership_number)
        if self.fob:
            personal_data['fob'] = int(self.fob)
        return personal_data
