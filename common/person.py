
class Person(object):

    def __init__(self, identification):
        # todo: find a person in the database
        pass

    def set_profile_field(self, fieldname, fieldvalue):
        # todo: set the field and write it back to the database
        pass

    def add_training(self, event):
        # todo: add the event to the appropriate role list of the person's training, and write it back to the database
        # note that the role can be found from the event
        pass

    def get_machines(self, role):
        # todo: get the list of the machines for which the person has that role
        pass

    def is_member(self):
        # todo: return whether the person is a member
        pass

    def is_administrator(self):
        # todo: return whether the person is an admin
        pass

    def is_inductor(self):
        # return whether the person is a general inductor
        pass

    def is_trained(self, machine):
        # return whether the person is trained to use that machine
        pass

    def is_owner(self, machine):
        # return whether the person is an owner of that machine
        pass

    def is_trained(self, machine):
        # return whether the person is a trainer for that machine
        pass
