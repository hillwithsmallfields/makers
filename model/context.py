from person import Person
import configuration

def set_context_from_django(context):
    # todo: talk to django to get the login context
    # Context.my_context.setup_context(get_id(django.getloggedinuser()))
    pass

class Context:

    """The viewing context of the logged-in user.
    This, and other users' visibility settings, determine when they can
    see other users' names."""

    my_context = None

    def __init__(self):
        self.link_id = None
        self.viewing_person = None
        self.roles = {'user': [],
                      'trainer': [],
                      'owner': []}
        self.admin = False
        self.auditor = False

    def add_role(self, role, equipment):
        self.roles[role].append(equipment)

    def setup_context(self, link_id):
        self.link_id = link_id
        self.viewing_person = Person.find(link_id)
        for role in self.roles.keys():
            for equipment in self.viewing_person.get_equipment_classes(role):
                self.add_role(role, equipment._id)
        self.cache_context()

    def cache_context(self):
        """Cache some context information.
        Call this after you've finished adding roles with add_role()."""
        org = configuration.get_config()['organization']['database']
        self.auditor = org in self.roles['user']
        self.admin = (self.auditor
                      or org in self.roles['owner']
                      or org in self.roles['trainer'])

    @staticmethod
    def get_context(callback=set_context_from_django):
        if Context.my_context is None:
            Context.my_context = Context()
            if callback:
                callback(Context.my_context)
                Context.my_context.cache_context()
        return Context.my_context

    @staticmethod
    def change_context(callback=set_context_from_django):
        if Context.my_context is None:
            Context.my_context = Context()
        else:
            Context.my_context.link_id = None
            Context.my_context.viewing_person = None
            Context.my_context.roles = {}
            Context.my_context.admin = False
            Context.my_context.auditor = False
        if callback:
            callback(Context.my_context)
            Context.my_context.cache_context()
        return Context.my_context

    def can_read_for(self, equipment_type):
        return (self.admin
                or self.auditor
                or (equipment_type and (equipment_type in self.roles['trainer']
                                  or equipment_type in self.roles['owner'])))

    def can_write_for(self, equipment_type):
        return (self.admin
                or (equipment_type and (equipment_type in self.roles['trainer']
                                   or equipment_type in self.roles['owner'])))
