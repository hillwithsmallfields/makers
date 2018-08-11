import model.access_permissions
import model.configuration
import model.database
import model.equipment_type
import model.event
import model.machine
import model.makers_server
import model.timeline
import model.person
from datetime import datetime, timedelta
import os
import uuid

# todo: induction input from jotform.com

class Person(object):

    """The Person class describes a person, typically but not necessarily a member.

    Some of the information that you might expect to be here is
    actually stored elsewhere, but you can access some of that through
    the methods of this class.

    In particular, what equipment a person is trained (authorized) to
    use is stored implictly, in the Events collection of the database,
    because a person is seen as trained if they have successfully
    attended a training event of the appropriate type.

    Also, a person's name and email address are not stored in the
    object, but accessed through methods.  This is because regulations
    require access to personally identifying information to be
    controlled, and the context for which a name is required must be
    given so that we can tell whether the information can be given in
    that context.

    The normal way to get a Person object is with the class method
    'find', which takes some kind of clue as to who you're looking
    for: name, email address, fob code, or mongodb ObjectId.

    """

    people_by_id = {}

    def __init__(self):
        self._id = None
        self.link_id = None
        self.api_authorization = None
        self.membership_number = None
        self.fob = None
        self.past_fobs = []
        self.training_requests = []      # list of dict with 'request_date', 'equipment_type' (as _id), 'event_type'
        self.training_requests_limit = None # normally comes from config but admins can override using this
        self.noshow_absolutions = 0
        self.available = 0xffffffff # bitmap of timeslots, lowest bit is Monday morning, etc
        self.invitations = {}       # dict of uuid to event
        self.visibility = {}        # binds 'general', 'host', 'attendee' to True, False, 'logged-in'
        self.stylesheet = None      # None means use the system default
        self.show_help = True
        self.notifications_read_to = datetime.utcnow()
        self.announcements_read_to = datetime.utcnow()

    def __str__(self):
        return ("<member " + str(self.membership_number)
                + " " + self.name()
                + ">")

    def __repr__(self):
        return "<member " + str(self.membership_number) + ">"

    @staticmethod
    def list_all_people():
        return [ model.person.Person.find(whoever) for whoever in model.database.get_all_person_dicts() ]

    @staticmethod
    def list_all_members():
        return model.equipment_type.Equipment_type.find(model.configuration.get_config()['organization']['name']).get_trained_users()

    @staticmethod
    def find(identification):
        """Find a person in the database."""
        data = identification if type(identification) is dict else model.database.get_person_dict(identification)
        if data is None:
            return None
        # convert the dictionary into a Person object
        person_id = data['_id']
        if person_id not in model.person.Person.people_by_id:
            model.person.Person.people_by_id[person_id] = Person()
        p = model.person.Person.people_by_id[person_id]
        p.__dict__.update(data)
        return p

    def visible(self,
                access_permissions_role=None,
                access_permissions_event=None,
                access_permissions_equipment=None):
        """Return whether this person's personal information, such as their name, is visible in a given context.

        The context may be given as a role (whether the viewing user
        is acting as an event host, for example), an event (to tell
        whether the host can see the attendees), and an equipment type
        (to tell whether the viewing user is an owner or trainer on
        that equipment, which may give them name viewing rights)."""
        # This line gets the information for the person logged in (the
        # "viewing person"), which is not necessarily the Person
        # object passed in as self:
        viewing_access_permissions = model.access_permissions.Access_Permissions.get_access_permissions()
        if (self == viewing_access_permissions.viewing_person
            or viewing_access_permissions.admin
            or viewing_access_permissions.auditor):
            return True
        visible_by_consent = self.visibility.get(access_permissions_role, False)
        return (viewing_access_permissions
                .viewing_person.can_read_for(self,
                                             # whether the viewing person is owner/trainer on that equipment:
                                             equipment_type=access_permissions_equipment,
                                             event=access_permissions_event)
                and (visible_by_consent == True
                     or (visible_by_consent == 'logged-in'
                         and viewing_access_permissions.viewing_person != None)))

    def name(self,
             access_permissions_event=None,
             access_permissions_role=None,
             access_permissions_equipment=None):
        """Return the person's name, unless they've requested anonymity."""
        if self.visible(access_permissions_event=access_permissions_event,
                        access_permissions_role=None,
                        access_permissions_equipment=None):
            formal, _ = model.database.person_name(self.link_id)
            return formal
        else:
            return ("member_"+str(self.membership_number))

    def nickname(self,
                 access_permissions_event=None,
                 access_permissions_role=None,
                 access_permissions_equipment=None):
        """Return the person's nickname, unless they've requested anonymity."""
        if self.visible(access_permissions_event=access_permissions_event,
                        access_permissions_role=None,
                        access_permissions_equipment=None):
            _, informal = model.database.person_name(self.link_id)
            return informal
        else:
            return ("member_"+str(self.membership_number))

    def get_email(self,
                  access_permissions_event=None,
                  access_permissions_role=None,
                  access_permissions_equipment=None):
        """Return the person's email, unless they've requested anonymity."""
        if self.visible(access_permissions_event=access_permissions_event,
                        access_permissions_role=None,
                        access_permissions_equipment=None):
            email = model.database.person_email(self.link_id,
                                          model.access_permissions.Access_Permissions.get_access_permissions().viewing_person)
            return email
        else:
            return ("member_"+str(self.membership_number)
                    +"@"+model.configuration.get_config()['server']['mailhost'])

    def get_visibility(self, access_permissions):
        return self.visibility[access_permissions]

    def set_visibility(self, access_permissions, level):
        self.visibility[access_permissions] = level

    def save(self):
        """Save the person to the database."""
        model.database.save_person(self.__dict__)

    def set_fob(self, newfob):
        if self.fob:
            self.past_fobs.append(self.fob)
        self.fob = newfob
        self.save()

    def get_profile_field(self, field_name,
                          access_permissions_event=None,
                          access_permissions_role=None,
                          access_permissions_equipment=None):
        """Get a field."""
        if self.visible(access_permissions_event=access_permissions_event,
                        access_permissions_role=None,
                        access_permissions_equipment=None):
            return model.database.get_person_profile_field(self, field_name)
        else:
            return None

    def set_profile_field(self, field_name, new_value):
        """Set a field and write it back to the database."""
        if self.visible(access_permissions_event=access_permissions_event,
                        access_permissions_role=None,
                        access_permissions_equipment=None):
            model.database.set_person_profile_field(self, field_name, new_value)

    # training and requests

    def get_training_requests_limit(self):
        """Get this person's open training request limit.
        If set to None, the system-wide defalt, from the config file, will be used."""
        return (self.training_requests_limit
                or int(model.configuration.get_config()['training']['default_max_requests']))

    def set_training_requests_limit(self, limit):
        """Set this person's open training request limit.
        If set to None, the system-wide defalt, from the config file, will be used."""
        self.training_requests_limit = limit
        self.save()

    def get_noshows(self):
        result = []
        for role in ['user', 'owner', 'trainer']:
            result += self.get_training_events(model.database.role_training(role), result='noshow')
        return result

    def absolve_noshows(self):
        """Administrator action to allow a person to continue to sign up for training,
        despite having been recorded as repeatedly wasting training slots."""
        self.noshow_absolutions = (len(self.get_training_events('user_training', result='noshow'))
                                   + len(self.get_training_events('owner_training', result='noshow'))
                                   + len(self.get_training_events('trainer_training', result='noshow')))
        self.save()

    def add_training_request(self, role, equipment_type, when=None):
        """Register a a training request for one or more equipment types.
        The time should not normally be specified, as that would allow
        queue-jumping, although an admin might do that if someone convinces
        them that they have a reasonable need for urgent training.
        The role may be 'user','trainer', or 'owner'."""
        if len(self.get_training_requests()) > self.get_training_requests_limit():
            return False, "Too many open training requests"
        role_training = model.database.role_training(role)
        if ((len(self.get_noshows()) - self.noshow_absolutions)
            >= int(model.configuration.get_config()['training']['no_shows_limit'])):
            return False, "Too many no-shows"
        for existing in self.training_requests:
            if equipment_type == existing['equipment_type']:
                return False, "Equipment type training already requested"
        self.training_requests.append({'request_date': when or datetime.utcnow(),
                                       'requester': self._id,
                                       'equipment_type': equipment_type._id,
                                       'event_type': role_training,
                                       'uuid': uuid.uuid4()})
        self.save()
        # todo: look for existing training events, and call this_event.invite_available_interested_people on them
        return True, None

    def remove_training_request(self, role, equipment_type):
        """Remove a training request."""
        event_type = model.database.role_training(role)
        for req in self.training_requests:
            if req['event_type'] == event_type and req['equipment_type'] == equipment_type._id:
                self.training_requests.remove(req)
                self.save()
                return True
        return False

    def alter_training_request_date(self, role, equipment_type, new_date):
        """Alter the date of a training request.
        This is to allow administrators to backdate training requests
        if a person convinces them that they have a good case for jumping
        the queue."""
        event_type = model.database.role_training(role)
        for req in self.training_requests:
            if req['event_type'] == event_type and equipment_type == req['equipment_type']:
                req['request_date'] = new_date
                return True
            self.save()
        return False

    def get_training_requests(self):
        keyed = { req['request_date']: req for req in self.training_requests }
        return [ keyed[d] for d in sorted(keyed.keys()) ]

    def has_requested_training(self, equipment_type, role):
        """Return whether the person has an unfulfilled training request
        for a given equipment and role."""
        event_type = model.database.role_training(role)
        for req in self.training_requests:
            if req['event_type'] == event_type and req.get('equipment_type',
                                                           # todo: remove this hack left for read compatibility with an earlier version
                                                           (req.get('equipment_types', ["compat-dummy"])[0])) == equipment_type:
                return req
        return None

    def get_training_events(self,
                            event_type='user_training',
                            when=None,
                            result='passed'):
        """Return the training data for this person,
        as a list of training events."""
        return model.database.get_events(event_type=event_type,
                                         person_field=result,
                                         person_id=self._id,
                                         include_hidden=True,
                                         latest=when)

    def add_training(self, tr_event):
        """Add the event to the appropriate role list of the person's events, and write it back to the database."""
        tr_event.mark_results([self], [], [])

    @staticmethod
    def awaiting_training(event_type, equipment_type):
        """List the people who have requested a particular type of training."""
        return map(model.person.Person.find,
                   model.database.get_people_awaiting_training(event_type, equipment_type))

    def mail_event_invitation(self, m_event, message_template_name):
        """Mail the person about an event.
        They get a link to click on to respond about whether they can attend."""
        invitation_uuid = str(uuid.uuid4())
        all_conf = model.configuration.get_config()
        server_config = all_conf['server']
        invitation_url = server_config['base_url'] + server_config['rsvp'] + invitation_uuid
        self.invitations[invitation_uuid] = m_event._id
        substitutions = {'rsvp': invitation_url,
                         'queue_position': len(m_event.invited),
                         'equipment_type': m_event.equipment_type,
                         'date': str(m_event.start)}
        with open(os.path.join(all_conf['messages']['templates_directory'], message_template_name)) as msg_file:
            makers_server.mailer(self.get_email(),
                                 msg_file.read() % substitutions)

    @staticmethod
    def mailed_event_details(rsvp):
        """Convert an RSVP UUID into a person and an event."""
        who = model.database.find_rsvp(rsvp)
        what = who['invitations'][rsvp]
        return model.person.Person.find(who._id), model.event.Event.find_by_id(what)

    def training_individual_event(self, admin_user,
                                  role, equipment_type, enabling,
                                  when=None, revert_after=None):
        """Add an individual training or untraining event.
        This is mostly for administrators to fix the record to match reality,
        and for banning and unbanning users."""
        if when is None:
            when = datetime.utcnow()
        special_event = model.event.Event(({'user': 'user_training',
                                            'owner': 'owner_training',
                                            'trainer': 'trainer_training'}
                                           if enabling
                                           else {'user': 'user_untraining',
                                                 'owner': 'owner_untraining',
                                                 'trainer': 'trainer_untraining'})[role], when,
                                          [admin_user._id], "Direct grant of permission" if enabling else "Ban",
                                          event_duration=0, # so it takes effect immediately
                                          signed_up=[self._id],
                                          equipment_type=equipment_type._id)
        special_event.mark_results([self], [], [])
        if revert_after and revert_after != "" and revert_after != "indefinite":
            self.training_individual_event(admin_user,
                                           role, equipment_type, not enabling,
                                           when=when+timedelta(int(revert_after), 0),
                                           revert_after=False)

    # Conditions and qualifications

    def get_equipment_types(self, role, when=None):
        """Get the list of the equipment_types for which the person has the specified role."""
        trained = {}
        detrained = {}
        for ev in self.get_training_events(event_type = model.database.role_training(role),
                                           when=when or datetime.utcnow()):
            trained[ev.equipment_type] = ev.start
        for ev in self.get_training_events(event_type = model.database.role_untraining(role),
                                           when=when or datetime.utcnow()):
            detrained[ev.equipment_type] = ev.start
        return [model.equipment_type.Equipment_type.find_by_id(e)
                for e in trained.keys()
                if (e not in detrained
                    or trained[e] > detrained[e])]

    def get_equipment_type_names(self, role):
        """Get the list of names of equipment types for which the person has a given role.
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
        """Return whether the person is qualified for a role on an equipment type.
        The first result is the event that qualified them, or None if they are not
        qualified or if their qualification is suspended.
        A second result gives their latest ban or suspension on this equipment type."""
        trained = None
        detrained = None
        equipment_id = model.equipment_type.Equipment_type.find(equipment_type_name)._id
        for ev in self.get_training_events(event_type = model.database.role_training(role),
                                           when=when or datetime.utcnow()):
            if equipment_id == ev.equipment_type:
                trained = ev
                break
        for ev in self.get_training_events(event_type = model.database.role_untraining(role),
                                           when=when or datetime.utcnow()):
            if equipment_id == ev.equipment_type:
                detrained = ev.start
                break
        if detrained is None:
            return trained, None
        if trained is None or detrained.start > trained.start:
            return None, detrained
        # skip_membership_check is for avoiding further recursion in the call to is_member.
        # Qualification to use equipment isn't cancelled immediately someone stops being a
        # member, so that if they restore their membership before the training is counted
        # as stale, the training can be retained as valid.  So in checking whether someone
        # can use a piece of equipment, we much also check that they are a member.
        if (not skip_membership_check) and (not self.is_member()[0]):
            return None, None
        return trained, detrained

    def is_member(self):
        """Return whether the person is a member, and whether they have a suspension on their membership."""
        return self.qualification(model.configuration.get_config()['organization']['name'], 'user',
                                  skip_membership_check=True)

    def is_administrator(self):
        """Return whether the person is an admin."""
        return self.is_owner(model.configuration.get_config()['organization']['database'])

    def is_auditor(self):
        """Return whether the person is an auditor.
        Similar to admin but read-only."""
        return self.is_trained(model.configuration.get_config()['organization']['database'])

    def is_inductor(self):
        """Return whether the person is a general inductor."""
        return self.is_trainer(model.configuration.get_config()['organization']['name'])

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
        """Takes a string describing one condition, and check the person meets that requirement.
        Sample strings are "laser-cutter user" and "mill trainer"."""
        equiptype, role = condition.split(' ')
        return self.qualification(equiptype, role)

    def satisfies_conditions(self, conditions, equipment_types):
        """Takes a list of strings describing one or more conditions, and check the person meets those requirements.

        This is used from Event.instantiate_template, to check whether
        the suggested hosts for an event have the necessary conditions
        (such as being trainers on equipment they plan to give
        training on).

        """
        for condition in conditions:
            if not self.satisfies_condition(condition, equipment_types):
                return False
        return True

    # Interests and skills

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

    # machine use

    def get_log_raw(self):
        return model.database.get_user_log(self._id)

    def get_log(self):
        return [ (str(entry['start']), model.machine.Machine.find(entry['machine'])) for entry in self.get_log_raw() ]

    # Update from form

    def update_profile(self, params):
        old_address = who.get_profile_field('address') or {}
        old_telephone = who.get_profile_field('telephone') or ""
        old_mugshot = who.get_profile_field('mugshot')
        old_email = who.get_email() # email needs special handling as we must tell django too
        # todo: fill this in
        # name needs special handling as we must tell django too

    def update_controls(self, params):
        # todo: fill this in
        pass

    # Announcements and notifications

    def read_announcements(self):
        up_to_time = datetime.utcnow()
        results = model.database.get_announcements(self.announcements_read_to)
        self.announcements_read_to = up_to_time
        return results

    def read_notifications(self):
        up_to_time = datetime.utcnow()
        results = model.database.get_notifications(self._id, self.notifications_read_to)
        self.notifications_read_to = up_to_time
        return results

    # API

    def api_personal_data(self, detailed=False):
        """Get the data for a person, in a suitable form for the API.
        With an optional flag, get more detail."""
        # todo: allow 'detailed' to be a list of fields you want
        name, known_as = model.database.person_name(self)
        personal_data = {'name': name,
                         'qualified': self.get_qualifications()}
        membership = self.is_member()[0]
        personal_data['member_since'] = str(membership.start.date())
        if known_as:
            personal_data['known_as'] = known_as
        if self.membership_number:
            personal_data['membership_number'] = int(self.membership_number)
        if self.fob:
            personal_data['fob'] = int(self.fob)
        if detailed:
            for field, title in [('hosts', 'hosting_events'), ('attendees', 'attending_events')]:
                my_events = model.timeline.Timeline.create_timeline(person_field=field, person_id=self._id).events
                if len(my_events) > 0:
                    my_event_api_data = [ { 'start': model.event.timestring(tl_event.start),
                                            'type': str(tl_event.event_type),
                                            'equipment_types': [ model.equipment_type.Equipment_type.find_by_id(eqty).name
                                                                    for eqty in tl_event.equipment_types]} for tl_event in my_events ]
                    personal_data[title] = my_event_api_data

            tr_hist = {}
            for role in ['user', 'owner', 'trainer']:
                for tr_ev in self.get_training_events(event_type = model.database.role_training(role)):
                    tr_hist[tr_ev.start] = tr_ev.event_as_json()
                for untr_ev in self.get_training_events(event_type = model.database.role_untraining(role)):
                    tr_hist[untr_ev.start] = untr_ev.event_as_json()
            personal_data['training_history'] = [ tr_hist[evdate] for evdate in sorted(tr_hist.keys()) ]
            personal_data['machine_log'] = [ [ str(entry[0]), entry[1].name ] for entry in self.get_log() ]
        return personal_data
