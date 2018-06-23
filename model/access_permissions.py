from person import Person
import configuration

def set_access_permissions_from_django(context):
    # todo: talk to django to get the login context
    # Access_Permissions.my_access_permissions.setup_access_permissions(get_id(django.getloggedinuser()))
    pass

class Access_Permissions(object):

    """The viewing access_permissions of the logged-in user.

    This, and other users' visibility settings, determine when they can
    see other users' names.

    This data is calculated when first used, and cached statically."""

    my_access_permissions = None # static cache of permissions

    def __init__(self):
        self.link_id = None
        self.viewing_person = None
        self.roles = {'user': [],
                      'trainer': [],
                      'owner': []}
        self.admin = False
        self.auditor = False

    def add_role(self, role, equipment):
        """Register that you have a particular role on a type of equipment.

        Normally used from setup_access_permissions."""
        self.roles[role].append(equipment)

    def setup_access_permissions(self, link_id):
        """Look through a person's roles and set up their permissions accordingly."""
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
        """Get the access permissions for the current user.

        A callback is used to get user-specific information from
        the web framework.

        The permission data is cached, so this can be used lightly."""
        if Access_Permissions.my_access_permissions is None:
            Access_Permissions.my_access_permissions = Access_Permissions()
            if callback:
                callback(Access_Permissions.my_access_permissions)
                Access_Permissions.my_access_permissions.cache_access_permissions()
        return Access_Permissions.my_access_permissions

    @staticmethod
    def change_access_permissions(callback=set_access_permissions_from_django):
        """Change the access permissions, as if changing user.

        Mostly useful for testing programs to check privacy handling."""
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

    def can_read_for(self, other, event=None, equipment_type=None):
        """Return whether this user can see another user's data, in the context of an event and an equipment type."""
        return (self.admin
                or self.auditor
                or other.visibility['general'] == True
                or (equipment_type is not None
                    and (equipment_type in self.roles['owner']
                         or (equipment_type in self.roles['trainer']
                             and event is not None
                             and self.viewing_person._id in event.hosts
                             and other._id in event.invitation_accepted
                             and other.visibility['attendee'] is not False))))

    def can_write_for(self, other, event=None, equipment_type=None):
        """Return whether this user can alter other users' data, in the context of an event and an equipment type."""
        return (self.admin
                or (equipment_type is not None
                    and (equipment_type in self.roles['owner']
                         or (equipment_type in self.roles['trainer']
                             and event is not None
                             and self.viewing_person._id in event.hosts
                             and other._id in event.invitation_accepted))))
