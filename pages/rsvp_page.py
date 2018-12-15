from untemplate.throw_out_your_templates_p3 import htmltags as T
import django.urls
import model.configuration
import model.database
import model.event
import model.makers_server
import model.person

server_conf = None

def invitation_response_form_page(rsvp_uuid):
    """From an invitation UUID that was mailed to someone, produce a response form."""
    global server_conf
    server_conf = configuration.get_config('server')
    page_pieces.set_server_conf()
    person_responding = person.Person.find(database.find_rsvp(rsvp_uuid))
    # set up viewing as though the user has actually logged in
    access_permissions.Access_Permissions.setup_access_permissions(person_responding.link_id)
    # todo: also tell django that they are effectively logged in?
    event_responding = event.Event.find_by_id(person_responding.invitations[rsvp_uuid])
    form_act = django.urls.reverse("events:rsvp_form", args=[rsvp_uuid])
    return T.div(class_="invitresp")[
        T.h1["RSVP for " + person_responding.name(access_permissions_event=event_responding)],
        T.p["This is a " + event_responding.event_type
            + " event starting at " + str(event_responding.start)
            + ".  The event will be hosted by "
            + ". and ".join([obj.name(access_permissions_role='host')
                             for obj in event_responding.hosts
                             if obj is not None])
            + "."],
        T.form(action=form_act,
               method='POST')[
            T.input(type="hidden",
                    name="rsvp_uuid",
                    value=rsvp_uuid),
            T.table(class_='unstriped')[
                T.tr[T.td[T.input(type='radio',
                                  name='rsvp',
                                  value='accept')],
                     T.td["Accept invitation"]],
                T.tr[T.td[T.input(type='radio',
                                  name='rsvp',
                                  value='decline')],
                     T.td["Decline invitation"]],
                T.tr[T.td[T.input(type='radio',
                                  name='rsvp',
                                  value='drop')],
                     T.td["Decline invitation and cancel training request"]]],
            T.input(type="submit", value="Send response")]]

def handle_invitation_response(rsvp_uuid, response):
    """Process an incoming reply from the form generated from a mailed invitation UUID."""
    global server_conf
    server_conf = configuration.get_config('server')
    page_pieces.set_server_conf()
    person_responding = person.Person.find(database.find_rsvp(rsvp_uuid))
    # set up viewing as though the user has actually logged in
    access_permissions.Access_Permissions.setup_access_permissions(person_responding.link_id)
    # todo: also tell django that they are effectively logged in?
    event_responding = event.Event.find_by_id(person_responding.invitations[rsvp_uuid])
    if response == 'accept':
        event_responding.add_invitation_accepted([person_responding])
        makers_server.generate_page('accepted', person_responding.name(), event_responding.title)
    elif response == 'decline':
        event_responding.add_invitation_declined([person_responding])
        makers_server.generate_page('declined', person_responding.name(), event_responding.title)
    elif response == 'drop':
        event_responding.add_invitation_declined([person_responding])
        person_responding.remove_training_request(event_responding.training_for_role(),
                                                  event_responding.equipment_type)
        makers_server.generate_page('dropped', person_responding.name(), event_responding.title)
    elif response == '':
        makers_server.generate_page('rsvp_choices', person_responding.name(), event_responding.title)
    else:
        makers_server.generate_page('rsvp_error', person_responding.name(), event_responding.title)
