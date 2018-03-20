#!/usr/bin/python

from nevow import flat
from nevow import tags as T
import configuration
import database
import pages

def event_host_qualified(event_details, person_making):
    """Return whether the specified event type can be scheduled by a particular person."""
    # todo: make a field of the event that points to an equp
    equipment = event_details['equipment']
    return (database.check_person_machine_role(person_making,
                                               equipment,
                                               'owner')
            or database.check_person_machine_role(person_making,
                                                  equipment,
                                                  'trainer')):

def event_type_selector_contents(event_type, person_making):
    """Make the form for selecting an event type.
The response to that form will bring up another page which has details
to fill in for that event type."""
    # todo: make the event creation data
    # This will use a template from the config
    conf = configuration.get_config()
    events_conf = conf['events']
    event_types = [ event.get('typename', "Unspecified --- FIXME")
                    for event in events_conf
                    if event_host_qualified(event, person_making) ]
    return []

def event_type_selector_page(event_type, person_making):
    return pages.page_string("Create " + event_type,
                             # todo: description list with radio buttons and explanatory text, and date/time selection, with submit button leading to event_creator_form_contents
                             event_type_selector_contents(event_type, person_making))

def event_creator_form_contents(event_type, person_making):
    """Make the form for getting details about an event, once the event type has been chosen."""
    # todo: make the event creation data
    # This will use a template from the config
    conf = configuration.get_config()
    event_conf = conf['events'][event_type]
    if not event_host_qualified(event_conf, person_making):
        return pages.error_page("Person not qualified to create event")
    return [
                             # todo: form for further details, depending on the event type
        ]

def event_creator_form_page(event_type, person_making):
    return pages.page_string("Create " + event_type,
                             event_creator_form_contents(event_type, person_making))

def event_creator_form_receiver_contents():
    """Process a completed event creation form, storing the results in the database."""
    # todo: fill in
    return []

def event_creator_form_receiver_page():
    return pages.page_string("Event created",
                             event_creator_form_receiver_contents())
