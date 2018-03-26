
class Equipment(object):

    def __init__(self, name):
        """Set up a machine's data, from its name."""
        # todo: get the machine's details from the database
        pass

    def get_equipment_class(self):
        """Return the equipment class of this equipment.
        Users, owners and trainers are reached through this, as they
        are related to all equipment of the same type rather than to a
        specific instance."""
        pass

    def get_maintenance_status(self):
        """Return whether the equipment is working, possibly with some detail."""
        pass

    def set_maintenance_status(self, flag, detail):
        """Indicate whether the equipment is working."""
        pass
