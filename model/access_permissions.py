from person import Person
import configuration

def set_access_permissions_from_django(context):
    # todo: talk to django to get the login context
    # Access_Permissions.my_access_permissions.setup_access_permissions(get_id(django.getloggedinuser()))
    pass

class Access_Permissions(object):

    """The viewing access_permissions of the logged-in user.
    This, and other users' visibility settings, determine when they can
    see other users' names."""

    my_access_permissions = None

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

    def setup_access_permissions(self, link_id):
        self.link_id = link_id
        self.viewing_person = Person.find(link_id)
        for role in self.roles.keys():
            for equipment in self.viewing_person.get_equipment_classes(role):
                self.add_role(role, equipment._id)
        self.cache_access_permissions()

    def cache_access_permissions(self):
        """Cache some access_permissions information.
        Call this after you've finished adding roles with add_role()."""
        org = configuration.get_config()['organization']['database']
        self.auditor = org in self.roles['user']
        self.admin = (self.auditor
                      or org in self.roles['owner']
                      or org in self.roles['trainer'])

    @staticmethod
    def get_access_permissions(callback=set_access_permissions_from_django):
        if Access_Permissions.my_access_permissions is None:
            Access_Permissions.my_access_permissions = Access_Permissions()
            if callback:
                callback(Access_Permissions.my_access_permissions)
                Access_Permissions.my_access_permissions.cache_access_permissions()
        return Access_Permissions.my_access_permissions

    @staticmethod
    def change_access_permissions(callback=set_access_permissions_from_django):
        if Access_Permissions.my_access_permissions is None:
            Access_Permissions.my_access_permissions = Access_Permissions()
        else:
            Access_Permissions.my_access_permissions.link_id = None
            Access_Permissions.my_access_permissions.viewing_person = None
            Access_Permissions.my_access_permissions.roles = {}
            Access_Permissions.my_access_permissions.admin = False
            Access_Permissions.my_access_permissions.auditor = False
        if callback:
            callback(Access_Permissions.my_access_permissions)
            Access_Permissions.my_access_permissions.cache_access_permissions()
        return Access_Permissions.my_access_permissions

    def can_read_for(self, equipment_type):
        return (self.admin
                or self.auditor
                or (equipment_type and (equipment_type in self.roles['trainer']
                                  or equipment_type in self.roles['owner'])))

    def can_write_for(self, equipment_type):
        return (self.admin
                or (equipment_type and (equipment_type in self.roles['trainer']
                                   or equipment_type in self.roles['owner'])))
