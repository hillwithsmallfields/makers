# -*- coding: utf8
from datetime import datetime, timedelta
from equipment_type import Equipment_type
import configuration
import database
import event
import person
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
                        if isinstance(clue, basestring)
                        else None)))


class Event(object):

    # keep a hash of events so each one is only in memory once
    events_by_id = {}

    def __init__(self, event_type,
                 event_datetime,
                 hosts,
                 title=None,
                 attendees=[],
                 event_duration=60,
                 equipment_types=[],
                 equipment=[]):
        """Create an event of a given type and datetime.
        The current user is added as a host.
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
        self.hosts = hosts         # _id of person
        self.attendance_limit = 30
        self.attendees = attendees # _id of person
        self.equipment_types = equipment_types
        self.equipment = equipment
        self._id = None
        self.passed = []   # _id of person
        self.failed = []   # _id of person
        self.noshow = []   # _id of person
        self.host_prerequisites = []
        self.attendee_prerequisites = []
        self.location = None
        self.catered = False
        self.interest_areas = []

    def __str__(self):
        accum = "<" + self.event_type
        starting = self.start
        if starting.hour == 0 and starting.minute == 0 and starting.second == 0:
            accum += "_event on " + str(starting.date())
        else:
            accum += "_event at " + str(starting)
        if self.hosts and self.hosts != []:
            accum += " with " + ", ".join([person.Person.find(host_id).name()
                                          for host_id in self.hosts
                                          if host_id is not None]).encode('utf-8')
        if self.equipment and self.equipment != []:
            accum += " on " + ", ".join([Equipment_type.find(e).name for e in self.equipment_types])
        if len(self.passed) > 0:
            accum += " passing " + ", ".join([person.Person.find(who).name() for who in self.passed])
        elif len(self.attendees) > 0:
            accum += " attending " + ", ".join([person.Person.find(who).name() for who in self.attendees])
        accum += ">"
        return accum

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def find(event_type, event_datetime, hosts, equipment_types):
        event_datetime = as_time(event_datetime)
        event_dict = database.get_event(event_type, event_datetime,
                                        hosts,
                                        equipment_types,
                                        create=True)
        if event_dict is None:
            return None
        event_id = event_dict['_id']
        if event_id not in Event.events_by_id:
            new_event_object = Event(event_type, event_datetime,
                                     hosts,
                                     attendees=[], # I don't know why I need to make this explicit, but if I don't, it keeps including all the previous ones
                                     equipment_types=equipment_types)
            Event.events_by_id[event_id] = new_event_object
        e = Event.events_by_id[event_id]
        e.__dict__.update(event_dict)
        return e

    @staticmethod
    def find_by_id(event_id):
        event_dict = database.get_event_by_id(event_id)
        if event_dict is None:
            return None
        if event_id not in Event.events_by_id:
            Event.events_by_id[event_id] = Event(event_dict['event_type'],
                                                 event_dict['start'],
                                                 event_dict['hosts'],
                                                 equipment_types=event_dict['equipment_types'])
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
        database.save_event(self.__dict__)

    @staticmethod
    def find_template(template_name):
        return database.find_event_template(template_name)

    @staticmethod
    def _preprocess_conditions_(raw_conds, equipment_types):
        """Typical conditions are an equipment type name followed by a role,
        such as "laser_cutter user" or "bandsaw owner".  The special equipment
        type name "$equipment" is expanded to all the equipment in the
        equipment_types argument.
        Also, a condition can be any of the strings "member", "admin",
        "auditor", or "director", which are given configuration-dependent expansions."""
        result = []
        for cond in raw_conds:
            if cond == "member":
                result.append(configuration.get_config()['organization']['name'] + " user")
            elif cond == "admin":
                result.append(configuration.get_config()['database']['database_name'] + " owner")
            elif cond == "auditor":
                result.append(configuration.get_config()['database']['database_name'] + " user")
            elif cond == "director":
                result.append(configuration.get_config()['organization']['name'] + " owner")
            elif ' ' not in cond:
                # really all the others should be two words, but just pass the
                # buck for now, someone might define a use for such a thing later
                result.append(cond)
            else:
                equiptypes, role = cond.split(' ')
                for onetype in (equipment_types
                                if equiptypes == "$equipment"
                                else equiptypes.split(';')):
                    result.append(Equipment_type.find(onetype).name + " " + role)
        return result

    def training_for_role(self):
        """Return the role for which this event gives training."""
        return (self.event_type[:-len("__training")]
                if self.event_type.endswith("_training")
                else None)

    @staticmethod
    def instantiate_template(template_name, equipment_types,
                             hosts, event_datetime, allow_past=False):
        """Instantiate a template, or explain the first reason to refuse to do so.
        Results are the resulting event instance, and the error; one of these will be None."""
        if event_datetime < datetime.now() and not allow_past:
            return None, "Cannot create a past event"
        template_dict = Event.find_template(template_name)
        # print "instantiate_template: template_dict is", template_dict
        host_prerequisites = Event._preprocess_conditions_(template_dict.get('host_prerequisites', ['member']),
                                                           equipment_types)
        for host in hosts:
            person_obj = person.Person.find(host)
            if not person_obj.satisfies_conditions(host_prerequisites, equipment_types):
                return None, person_obj.name() + " is not qualified to host this event"
        attendee_prerequisites = Event._preprocess_conditions_(template_dict.get('attendee_prerequisites', []),
                                                               equipment_types)
        title = template_dict['title'].replace("$equipment",
                                               ", ".join([Equipment_type.find(eqty).name
                                                          for eqty in equipment_types]))
        instance = Event(template_dict['event_type'],
                         event_datetime,
                         hosts,
                         title=title,
                         attendees=[],
                         equipment_types=equipment_types)
        instance.__dict__.update(template_dict)
        instance.host_prerequisites = host_prerequisites
        instance.attendee_prerequisites = attendee_prerequisites
        return instance, None

    @staticmethod
    def _all_hosts_suitable_(template_dict, hosts, equipment_types):
        host_conds = Event._preprocess_conditions_(template_dict.get('host_prerequisites', ['member']),
                                                   equipment_types)
        # print "checking", hosts, "against", template_dict, "using conditions", host_conds
        for host in hosts:
            x = person.Person.find(host)
            if not x.satisfies_conditions(host_conds, equipment_types):
                # print x, "does not satisfy", host_conds
                return False
        return True

    @staticmethod
    def list_templates(hosts, equipment_types):
        """Return the list of event templates for which all the specified hosts
        have all the hosting prerequisites."""
        return [ template for template in database.list_event_templates()
                 if Event._all_hosts_suitable_(template, hosts, equipment_types) ]

    def notify_interested_people(self):
        timeslot = as_timeslot(self.start)
        for person in person.awaiting_training(self.event_type, self.equipment_types):
            if person.available & timeslot:
                person.notify(self)

    def publish(self):
        """Make the event appear in the list of scheduled events."""
        self.status = 'published'
        self.save()

    def unpublish(self):
        """Stop the event appearing in the list of scheduled events."""
        self.status = 'concealed'
        self.save()

    @staticmethod
    def future_events():
        """List the events which have not yet started."""
        return None

    @staticmethod
    def present_events():
        """List the events which have started but not finished."""
        return None

    @staticmethod
    def past_events():
        """List the events which have finished."""
        return None

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

    def get_attendees(self):
        """Return the list of people attending the event."""
        return [ person.Person.find(at_id) for at_id in self.attendees ]

    def add_attendees(self, attendees):
        """Add specified people to the attendees list."""
        # print "event", self._id, "adding", attendees, "to", self.attendees, "?"
        for attendee in attendees:
            if attendee._id not in self.attendees:
                # print "yes, adding", attendee, attendee._id
                self.attendees.append(attendee._id)
        self.save()

    def remove_attendees(self, attendees):
        """Remove specified people from the attendees list."""
        for attendee in attendees:
            if attendee._id in self.attendees:
                self.attendees.remove(attendee._id)
        self.save()

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
        for person_id in self.attendees:
            whoever = person.Person.find(person_id)
            if whoever and 'avoidances' in whoever.profile:
                avoids = ", ".join(sorted(whoever.profile['avoidances']))
                avoidances[avoids] = avoidances.get(avoids, 0) + 1
        return avoidances

    def dietary_avoidances_summary(self):
        """Return the dietary avoidance data as an alphabetically sorted list of pairs of avoidance to number of advoidents."""
        avoidances = self.dietary_avoidances()
        return [ (avkey, avoidances[avkey]) for avkey in sorted(avoidances.keys()) ]

    def possibly_interested_people(self):
        return database.find_interested_people(self.interest_areas)
    
    def save_as_template(self, name):
        """Save this event as a named template."""
        pass

    def event_as_json(self):
        result = {'event_type': self.event_type,
                  'equipment_types': [ Equipment_type.find_by_id(eqty).name for eqty in self.equipment_types ] }
        starting = self.start
        if starting.hour == 0 and starting.minute == 0 and starting.second == 0:
            result['date'] = str(starting.date())
        else:
            result['start'] = str(starting)
            result['end'] = str(self.end)
        # todo: add hosts if their privacy setting permit it
        return result

def as_id(event):
    """Given an event or id, return the id."""
    return event._id if type(event) == Event else event

def as_event(event):
    """Given an event or id, return the event."""
    return event if type(event) == Event else Event.events_by_id.get(event, None)
