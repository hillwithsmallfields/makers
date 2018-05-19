import event
import person

class Rsvp(Object):
    
    def handle_invitation_response(self, person, event, response):
        """Process an incoming reply."""
        if response == 'accept':
            event.add_attendees([person._id])
            return True
        elif response == 'decline':
            event.remove_attendees([person._id])
            return True
        elif response == 'drop':
            event.remove_attendees([person._id])
            person.remove_training_request(role, equipment_types)
            return True
        elif response == '':
            pass                # todo: create a web page with buttons for the choices
            return True
        else:
            return False
        
