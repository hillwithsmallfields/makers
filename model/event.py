# -*- coding: utf8
from datetime import datetime, timedelta
import model.access_permissions
import model.configuration
import model.database
import model.equipment_type
import model.pages
import model.person
import model.timeslots
import re

# todo: event templates to have after-effect fields, so that cancellation of membership can schedule cancellation of equipment training

fulltime = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}[T ][0-9]{2}:[0-9]{2}:[0-9]{2}")

def as_time(clue):
    return (clue
            if isinstance(clue, datetime)
            else (datetime.fromordinal(clue)
                  if isinstance(clue, int)
                  else (datetime.strptime(clue, "%Y-%m-%dT%H:%M:%S"
                                          if fulltime.match(clue)
                                          else "%Y-%m-%d")
                        if isinstance(clue, str)
                        else None)))

def timestring(when):
    if when.hour == 0 and when.minute == 0 and when.second == 0:
        return str(when.date())
    else:
        when.replace(microsecond=0)
        if when.second >= 59:
            when.replace(minute=when.minute + 1)
            when.replace(second=0)
        return str(when)[:16]

class Event(object):

    """The event class is used for past, present and future events.

    Past events form the connection between people and equipment
    types, by keeping the record of who has attended what kinds of
    training.

    Future events are used to inform people about what is coming up.

    Training events are what the whole system is centred around, but,
    having got an Event class, we also use it for all other kinds of
    events, such as talks and socials.

    Events have equipment types associated with them, which mostly
    apply to training events.

    As well as training events, there can also be untraining events,
    to cancel training; this is used to ban people from using
    equipment that they've misused.

    Events are normally created by instantiating event templates, and
    existing events can be found from the database using the class
    methods 'find' and 'find_by_id'.

    Event templates haven't quite made it into being an object class
    of their own; for now, they are just dictionaries.

    """

    # keep a hash of events so each one is only in memory once
    events_by_id = {}

    def __init__(self, event_type,
                 event_datetime,
                 hosts,
                 title=None,
                 signed_up=[],
                 event_duration=60,
                 equipment_type=None,
                 equipment=[]):
        """Create an event of a given type and datetime.

        The event is not saved and scheduled yet."""
        # self.details = get_event_template(event_type)
        self.title = title
        self.event_type = event_type
        self.start = as_time(event_datetime)
        self.end = self.start + (event_duration
                                 if isinstance(event_duration, timedelta)
                                 else (timedelta(0, event_duration * 60) # given in minutes
                                       if isinstance(event_duration, int)
                                       else timedelta(0, 120 * 60)))
        self.status = 'draft'
        # It would be nice to use Python sets for these,
        # but then we'd have to convert them for loading and saving in mongo.
        self.hosts = hosts         # [_id of person]
        self.attendance_limit = 30
        self.signed_up = signed_up # [_id of person]
        self.invited = {}          # {_id of person: timestamp of invitation}
        self.invitation_declined = []         # [_id of person]
        self.invitation_timeout = 3           # days
        self.equipment_type = model.pages.unstring_id(equipment_type)
        self.equipment = equipment # list of Machine, by ObjectId
        self._id = None
        self.passed = []    # [_id of person]
        self.failed = []    # [_id of person]
        self.noshow = []    # [_id of person]
        self.host_prerequisites = []
        self.attendee_prerequisites = []
        self.location = None
        self.catered = False
        self.alchohol_authorized = False
        self.interest_areas = []

    def __str__(self):
        accum = "<" + self.event_type + "_event " + timestring(self.start)
        if self.hosts and self.hosts != []:
            accum += " with " + ", ".join([model.person.Person.find(host_id).name()
                                          for host_id in self.hosts
                                          if host_id is not None])
        if self.equipment and self.equipment != []:
            accum += " on " + model.equipment_type.Equipment_type.find(self.equipment_type).name
        if len(self.passed) > 0:
            accum += " passing " + ", ".join([model.person.Person.find(who).name() for who in self.passed])
        elif len(self.signed_up) > 0:
            accum += " attending " + ", ".join([model.person.Person.find(who).name() for who in self.signed_up])
        accum += ">"
        return accum

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def find(event_type, event_datetime, hosts, equipment_type):
        """Find an event by giving enough information to describe it."""
        event_datetime = as_time(event_datetime)
        event_dict = model.database.get_event(event_type, event_datetime,
                                        hosts,
                                        model.pages.unstring_id(equipment_type),
                                        create=True)
        if event_dict is None:
            return None
        event_id = event_dict['_id']
        if event_id not in Event.events_by_id:
            new_event_object = Event(event_type, event_datetime,
                                     hosts,
                                     signed_up=[], # I don't know why I need to make this explicit, but if I don't, it keeps including all the previous ones
                                     equipment_type=equipment_type)
            Event.events_by_id[event_id] = new_event_object
        e = Event.events_by_id[event_id]
        e.__dict__.update(event_dict)
        return e

    @staticmethod
    def find_by_id(event_id):
        """Find an event by its ObjectId."""
        event_id = model.pages.unstring_id(event_id)
        event_dict = model.database.get_event_by_id(event_id)
        if event_dict is None:
            return None
        if event_id not in Event.events_by_id:
            Event.events_by_id[event_id] = Event(event_dict['event_type'],
                                                 event_dict['start'],
                                                 event_dict['hosts'],
                                                 equipment_type=event_dict.get('equipment_type', None))
        e = Event.events_by_id[event_id]
        e.__dict__.update(event_dict)
        return e

    def get_details(self):
        """Get the details of an event, as a dictionary."""
        return self.__dict__

    def set_details(self, details_dict):
        """Set the details of an event, from a dictionary."""
        self.__dict__.update(details_dict)

    def save(self):
        """Save the event to the database."""
        model.database.save_event(self.__dict__)
        # todo: remove debugging hack
        print("saved event", self.__dict__)

    @staticmethod
    def find_template(template_name):
        """Get an event template, by name."""
        return model.database.find_event_template(template_name)

    @staticmethod
    def write_template(template_name, template_dict):
        """Save an event template, to a given name."""
        template_dict['title'] = template_name
        model.database.add_template(template_dict)

    @staticmethod
    def _preprocess_conditions_(raw_conds, equip_type):
        """Make some substitutions in condition descriptions of event templates.

        Typical conditions are an equipment type name followed by a role,
        such as "laser_cutter user" or "bandsaw owner".  The special equipment
        type name "$equipment" is expanded to the equipment in the
        equip_type argument.

        Also, a condition can be any of the strings "member", "admin",
        "auditor", or "director", which are given configuration-dependent expansions."""
        result = []
        for cond in raw_conds:
            if cond == "member":
                result.append(model.configuration.get_config()['organization']['name'] + " user")
            elif cond == "admin":
                result.append(model.configuration.get_config()['database']['database_name'] + " owner")
            elif cond == "auditor":
                result.append(model.configuration.get_config()['database']['database_name'] + " user")
            elif cond == "director":
                result.append(model.configuration.get_config()['organization']['name'] + " owner")
            elif ' ' not in cond:
                # really all the others should be two words, but just pass the
                # buck for now, someone might define a use for such a thing later
                result.append(cond)
            else:
                onetype, role = cond.split(' ')
                if onetype == "$equipment":
                    onetype = equip_type
                type_descr = model.equipment_type.Equipment_type.find(onetype)
                print("onetype is", onetype, "of type", type(onetype), "and type_descr is", type_descr)
                result.append(type_descr.name + " " + role)
        return result

    def training_for_role(self):
        """Return the role for which this event gives training."""
        return (self.event_type[:-len("__training")]
                if self.event_type.endswith("_training")
                else None)

    @staticmethod
    def instantiate_template(template_name, equipment_type,
                             hosts, event_datetime, machines=[], allow_past=False):
        """Instantiate a template, or explain the first reason to refuse to do so.

        Event templates are stored in a separate database collection.
        They can define the fields 'host_prerequisites',
        'attendee_prerequisites', 'title', 'event_type'; any other
        fields in them will be copied into the dictionary representing
        the event.

        Results are the resulting event instance, and the error; one of these will be None.

        """
        if isinstance(event_datetime, str):
            event_datetime = datetime.strptime(event_datetime, "%Y-%m-%dT%H:%M")
        if event_datetime < datetime.now() and not allow_past:
            return None, "Cannot create a past event"
        template_dict = Event.find_template(template_name)
        print("instantiate_template: template_dict is", template_dict)
        if template_dict is None:
            return None, "Could not find a template called " + template_name
        host_prerequisites = Event._preprocess_conditions_(template_dict.get('host_prerequisites',
                                                                             ['member']),
                                                           equipment_type)
        for host in hosts:
            person_obj = model.person.Person.find(host)
            if not person_obj.satisfies_conditions(host_prerequisites, equipment_type):
                return None, person_obj.name() + " is not qualified to host this event"
        attendee_prerequisites = Event._preprocess_conditions_(template_dict.get('attendee_prerequisites',
                                                                                 []),
                                                               equipment_type)
        print("equipment_type is", equipment_type, "of type", type(equipment_type))
        title = template_dict['title'].replace("$equipment", model.equipment_type.Equipment_type.find(equipment_type).name)

        instance = Event(template_dict['event_type'],
                         event_datetime,
                         hosts,
                         title=title,
                         signed_up=[],
                         equipment_type=equipment_type)

        instance_dict = model.database.get_event(template_dict['event_type'],
                                                 event_datetime,
                                                 hosts,
                                                 equipment_type, True)

        instance_dict['equipment'] = machines

        instance.__dict__.update(instance_dict)

        for k, v in template_dict.items():
            if instance.__dict__.get(k, None) is None:
                instance.__dict__[k] = v
        instance.end = instance.start + timedelta(0, 60 * int(template_dict.get('duration', '120')))
        instance.host_prerequisites = host_prerequisites
        instance.attendee_prerequisites = attendee_prerequisites
        instance.save()
        return instance, None

    @staticmethod
    def _all_hosts_suitable_(template_dict, hosts, equipment_type):
        """Check that all the suggested hosts for an event are suitably qualified.

        For example, a training event should specify that all its hosts are trainers."""
        host_conds = Event._preprocess_conditions_(template_dict.get('host_prerequisites', ['member']),
                                                   equipment_type)
        for host in hosts:
            x = model.person.Person.find(host)
            if not x.satisfies_conditions(host_conds, equipment_type):
                return False
        return True

    @staticmethod
    def list_templates(hosts, equipment_type):
        """Return the list of event templates for which all the specified hosts have all the hosting prerequisites.

        The normal use of this will be with a single host specified,
        to generate the list of events that a user can create, on
        their dashboard page."""
        return [ template for template in model.database.list_event_templates()
                 if Event._all_hosts_suitable_(template, hosts, equipment_type) ]

    def available_interested_people(self):
        event_timeslot_bitmap = model.timeslots.time_to_timeslot(self.start)
        return [whoever
                for whoever in model.person.Person.awaiting_training(self.event_type, self.equipment_type)
                if whoever.available & event_timeslot_bitmap]

    def invite_available_interested_people(self):
        """Send event invitations to the relevant people.
        These are those who:
          - have expressed an interest
          - have indicated they may be available at that time
          - have not yet been invited, or have replied to an invitation."""
        self.auto_expire_non_replied_invitations()
        if len(self.signed_up) < self.attendance_limit:
            potentials = [whoever for whoever in self.available_interested_people()
                          if (whoever._id not in self.signed_up
                              and whoever._id not in self.invitation_declined)]
            if len(potentials) > self.attendance_limit:
                potentials = potentials[:self.attendance_limit]
            for whoever in potentials:
                if whoever._id not in self.invited:
                    whoever.mail_event_invitation(self, "training_invitation")
                    self.invited[whoever._id] = datetime.now()

    def publish(self):
        """Make the event appear in the list of scheduled events."""
        self.status = 'published'
        self.save()

    def unpublish(self):
        """Stop the event appearing in the list of scheduled events."""
        self.status = 'concealed'
        self.save()

    def get_hosts(self):
        """Return the list of people hosting the event."""
        return self.hosts

    def add_hosts(self, hosts):
        """Add specified hosts to the hosts list."""
        for host in hosts:
            if host._id not in self.hosts:
                self.hosts.append(host._id)
        self.save()

    def remove_hosts(self, hosts):
        """Remove specified hosts from the hosts list."""
        for host in hosts:
            if host in self.hosts:
                self.hosts.remove(host._id)
        self.save()

    def get_signed_up(self):
        """Return the list of people attending the event."""
        return [ model.person.Person.find(at_id) for at_id in self.signed_up ]

    def add_signed_up(self, signed_up):
        """Add specified people to the signed_up list."""
        # print "event", self._id, "adding", signed_up, "to", self.signed_up, "?"
        for attendee in signed_up:
            if attendee._id not in self.signed_up:
                # print "yes, adding", attendee, attendee._id
                self.signed_up.append(attendee._id)
        self.remove_invitation_declined(signed_up)
        self.save()

    def remove_signed_up(self, signed_up):
        """Remove specified people from the signed_up list."""
        for attendee in signed_up:
            if attendee._id in self.signed_up:
                self.signed_up.remove(attendee._id)
        self.save()

    def add_invitation_declined(self, invitation_declined):
        """Add specified people to the invitation_declined list."""
        # print "event", self._id, "adding", invitation_declined, "to", self.invitation_declined, "?"
        for attendee in invitation_declined:
            if attendee._id not in self.invitation_declined:
                # print "yes, adding", attendee, attendee._id
                self.invitation_declined.append(attendee._id)
        self.remove_signed_up(invitation_declined)
        self.save()

    def remove_invitation_declined(self, invitation_declined):
        """Remove specified people from the invitation_declined list."""
        for attendee in invitation_declined:
            if attendee._id in self.invitation_declined:
                self.invitation_declined.remove(attendee._id)
        self.save()

    def auto_expire_non_replied_invitations(self):
        cutoff = datetime.now() - timedelta(self.invitation_timeout,0)
        for who, when in self.invited.items():
            if when < cutoff:
                if (who._id not in self.signed_up
                    and who._id not in self.invitation_declined):
                    self.invitation_declined.append(who._id)

    def mark_results(self, successful, failed, noshow):
        """Record the results of a training session."""
        for whoever in successful:
            if whoever._id not in self.passed:
                self.passed.append(whoever._id)
        for whoever in failed:
            if whoever._id not in self.failed:
                self.failed.append(whoever._id)
        for whoever in noshow:
            if whoever._id not in self.noshow:
                self.noshow.append(whoever._id)
        self.save()

    def dietary_avoidances(self):
        """Return the dietary avoidance data as a dictionary of avoidance to number of advoidents."""
        avoidances = {}
        for person_id in self.signed_up:
            whoever = model.person.Person.find(person_id)
            if whoever and 'avoidances' in whoever.profile:
                avoids = ", ".join(sorted(whoever.profile['avoidances']))
                avoidances[avoids] = avoidances.get(avoids, 0) + 1
        return avoidances

    def dietary_avoidances_summary(self):
        """Return the dietary avoidance data as an alphabetically sorted list of pairs of avoidance to number of advoidents."""
        avoidances = self.dietary_avoidances()
        return [ (avkey, avoidances[avkey]) for avkey in sorted(avoidances.keys()) ]

    def possibly_interested_people(self):
        return model.database.find_interested_people(self.interest_areas)

    def save_as_template(self, name):
        """Save this event as a named template."""
        pass

    def event_as_json(self):
        result = {'event_type': self.event_type,
                  'equipment_type': [ Equipment_type.find_by_id(eqty).name for eqty in self.equipment_type ] }
        starting = self.start
        if starting.hour == 0 and starting.minute == 0 and starting.second == 0:
            result['date'] = str(starting.date())
        else:
            result['start'] = str(starting)
            result['end'] = str(self.end)
        hosts = []
        logged_in = model.access_permissions.Access_Permissions.get_access_permissions().viewing_person is not None
        for h in self.hosts:
            host = model.person.Person.find(h)
            if host is None:
                continue
            visibility = host.visibility.get('host', False)
            if visibility == True or (visibility == 'logged-in' and logged_in):
                hosts.append(host)
        if len(hosts) > 0:
            result['hosts'] = hosts
        return result

def as_id(event):
    """Given an event or id, return the id."""
    return event._id if type(event) == Event else event

def as_event(event):
    """Given an event or id, return the event."""
    return event if type(event) == Event else Event.events_by_id.get(event, None)
