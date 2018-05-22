import database
import timeline
import event
import equipment_type
import configuration
import equipment_type
import uuid
import os
import makers_server
from datetime import datetime

# todo: induction input from jotform.com

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
        self.invitations = {}       # dict of uuid to event
        self.profile = {} # bag of stuff like skills, demographic info, foods they avoid

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

    def name(self, context_role=None, context_equipment=None):
        """Return the person's name, unless they've requested anonymity."""
        formal, _ = database.person_name(self.link_id, role_viewed=context_role, equipment=context_equipment)
        return formal.encode('utf-8')

    def nickname(self):
        """Return the person's nickname, unless they've requested anonymity."""
        _, informal = database.person_name(self.link_id, role_viewed=context_role, equipment=context_equipment)
        return informal.encode('utf-8')

    def save(self):
        """Save the person to the database."""
        database.save_person(self.__dict__)

    def set_fob(self, newfob):
        self.fob = newfob
        self.save()

    def set_profile_field(self, **kwargs):
        """Set the fields and write them back to the database."""
        self.profile.update(kwargs)
        self.save()

    # training and requests

    def get_training_requests_limit(self):
        return (self.training_requests_limit
                or int(configuration.get_config()['training']['default_max_requests']))

    def set_training_requests_limit(self, limit):
        """Set this person's open training request limit.
        If set to None, the system-wide defalt, from the config file, will be used."""
        self.training_requests_limit = limit
        self.save()

    def absolve_noshows(self):
        """Administrator action to allow a user to continue to sign up for training,
        despite having been recorded as repeatedly wasting training slots."""
        self.noshow_absolutions = (len(self.get_training_events('user_training', result='noshow'))
                                   + len(self.get_training_events('owner_training', result='noshow'))
                                   + len(self.get_training_events('trainer_training', result='noshow')))
        self.save()

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

    def remove_training_request(self, role, equipment_types):
        """Remove a training request."""
        event_type = database.role_training(role)
        for req in self.requests:
            if req['event_type'] != event_type:
                continue
            if equipment_type == req['equipment_types']:
                self.requests.remove(req)
                return True
            self.save()
        return False

    def alter_training_request_date(self, role, equipment_types, new_date):
        """Alter the date of a training request.
        This is to allow administrators to backdate training requests
        if a user convinces them that they have a good case for jumping
        the queue."""
        event_type = database.role_training(role)
        for req in self.requests:
            if req['event_type'] != event_type:
                continue
            if equipment_type == req['equipment_types']:
                req['request_date'] = new_date
                return True
            self.save()
        return False

    def get_training_requests(self):
        keyed = { req['request_date']: req for req in self.requests }
        return [ keyed[d] for d in sorted(keyed.keys()) ]

    def has_requested_training(self, equipment_types, role):
        event_type = database.role_training(role)
        for req in self.requests:
            if req['event_type'] != event_type:
                continue
            for eqty in req['equipment_types']:
                if eqty in equipment_types:
                    return req
        return None

    def get_training_events(self,
                            event_type='user_training',
                            when=None,
                            result='passed'):
        """Return the training data for this user,
        as a list of training events."""
        # todo: handle the when parameter; I think there is a bug in database.get_events such that it doesn't find the training if we pass that argument on
        return database.get_events(event_type=event_type,
                                   person_field=result,
                                   person_id=self._id,
                                   include_hidden=True
                                   # ,as_recently_as=when
        )

    def add_training(self, tr_event):
        """Add the event to the appropriate role list of the person's events, and write it back to the database."""
        tr_event.mark_results([self], [], [])

    @staticmethod
    def awaiting_training(event_type, equipment_types):
        """List the people who have requested a particular type of training."""
        return database.get_people_awaiting_training(event_type, equipment_types)

    def mail_event_invitation(self, m_event, message_template_name):
        """Mail the user about an event.
        They get a link to click on to respond about whether they can attend."""
        invitation_uuid = str(uuid.uuid4())
        all_conf = configuration.get_config()
        server_config = all_conf['server']
        invitation_url = server_config['base_url'] + server_config['rsvp'] + invitation_uuid
        self.invitations[invitation_uuid] = m_event._id
        substitutions = {'rsvp': invitation_url,
                         'equipment_types': ', '.join([ equipment_type.Equipment_type.find_by_id(eqty).name
                                                        for eqty
                                                        in m_event.equipment_types ]),
                         'date': str(m_event.start)}
        with open(os.path.join(all_conf['messages']['templates_directory'], message_template_name)) as msg_file:
            makers_server.mailer(self.email,
                                 msg_file.read() % substitutions)

    @staticmethod
    def mailed_event_details(rsvp):
        """Convert an RSVP UUID into a person and an event."""
        who = database.find_rsvp(rsvp)
        what = who['invitations'][rsvp]
        return Person.find(who._id), event.Event.find_by_id(what)

    # Conditions and qualifications

    def get_equipment_types(self, role, when=None):
        """Get the list of the equipment_classes for which the person has the specified role."""
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

    def get_equipment_type_names(self, role):
        """Get the list of equipment types for which the user has a given role.
        Aimed mostly at the JSON API."""
        return [ eq.name for eq in self.get_equipment_types(role) ]

    def get_qualifications(self, detailed=False):
        # aimed at JSON API
        quals = {}
        for role in ['user', 'owner', 'trainer']:
            q = self.get_equipment_type_names(role)
            if q:
                quals[role] = quals.get(role, []) + q
        return quals

    def qualification(self, equipment_type_name, role,
                      when=None,
                      skip_membership_check=False):
        """Return whether the user is qualified for a role on an equipment class.
        The result is the event that qualified them."""
        trained = None
        detrained = None
        equipment_id = equipment_type.Equipment_type.find(equipment_type_name)._id
        for ev in self.get_training_events(event_type = database.role_training(role),
                                           when=when or datetime.now()):
            if equipment_id in ev.equipment:
                trained = ev
                break
        for ev in self.get_training_events(event_type = database.role_untraining(role),
                                           when=when or datetime.now()):
            if equipment_id in ev.equipment:
                detrained = ev.start
                break
        if detrained is None:
            return trained
        if trained is None or detrained.start > trained.start:
            return None
        # skip_membership_check is for avoiding further recursion in the call to is_member.
        # Qualification to use equipment isn't cancelled immediately someone stops being a
        # member, so that if they restore their membership before the training is counted
        # as stale, the training can be retained as valid.  So in checking whether someone
        # can use a piece of equipment, we much also check that they are a member.
        if (not skip_membership_check) and (not self.is_member()):
            return None
        return trained

    def is_member(self):
        """Return whether the person is a member."""
        return self.qualification(configuration.get_config()['organization']['name'], 'user',
                                  skip_membership_check=True)

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

    def satisfies_condition(self, condition, equipment_types):
        equiptype, role = condition.split(' ')
        return self.qualification(equiptype, role)

    def satisfies_conditions(self, conditions, equipment_types):
        for condition in conditions:
            if not self.satisfies_condition(condition, equipment_types):
                return False
        return True

    def get_interests(self):
        return self.profile.get('interests', {})

    def add_interest(self, interest, level):
        """Interest levels are:
        0: no interest
        1: would like to learn
        2: already learnt
        3: can teach"""
        if 'interests' in self.profile:
            self.profile['interests'][interest] = level
        else:
            self.profile['interests'] = {interest: level}
        self.save()

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
        if detailed:
            tr_hist = {}
            for role in ['user', 'owner', 'trainer']:
                for tr_ev in self.get_training_events(event_type = database.role_training(role)):
                    tr_hist[tr_ev.start] = tr_ev.event_as_json()
                for untr_ev in self.get_training_events(event_type = database.role_untraining(role)):
                    tr_hist[untr_ev.start] = untr_ev.event_as_json()
            personal_data['training_history'] = [ tr_hist[evdate] for evdate in sorted(tr_hist.keys()) ]
            # todo: add the training sessions they have hosted
            # todo: add non-training sessions they've attended or hosted
            # todo: add device use history, once we start logging that
        return personal_data
