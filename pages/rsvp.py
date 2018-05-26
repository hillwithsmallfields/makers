import event
import makers_server
import person

class Rsvp(Object):

    def handle_invitation_response(self, person, event, response):
        """Process an incoming reply."""
        if response == 'accept':
            event.add_attendees([person._id])
            makers_server.generate_page('accepted', person, event)
        elif response == 'decline':
            event.remove_attendees([person._id])
            makers_server.generate_page('declined', person, event)
        elif response == 'drop':
            event.remove_attendees([person._id])
            person.remove_training_request(event.training_for_role(),
                                           event.equipment_types)
            makers_server.generate_page('dropped', person, event)
        elif response == '':
            makers_server.generate_page('rsvp_choices', person, event)
        else:
            makers_server.generate_page('rsvp_error', person, event)
