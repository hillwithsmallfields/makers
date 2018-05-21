import database

class Machine(object):

    machine_by_id = {}
    machine_by_name = {}

    def __init__(self, name, equipment_type):
        """Set up a machine's data, from its name."""
        self.name = name
        self.equipment_type = equipment_type
        self.status = 'unknown'
        self.maintenance_history = []
        self.maintenance_due = None
        self.Location = None
        self.brand = None
        self.model = None
        self.acquired = None

    @staticmethod
    def find(name):
        if isinstance(name, Machine):
            return name
        if name in Machine.machine_by_name:
            return Machine.machine_by_name[name]
        data = database.get_machine_dict(name)
        if data is None:
            return None
        c = Machine()
        c.__dict__.update(data)
        Machine.machine_by_id[data['_id']] = c
        Machine.machine_by_name[data['name']] = c
        return c

    @staticmethod
    def find_by_id(id):
        if id in Machine.machine_by_id:
            return Machine.machine_by_id[id]
        data = database.get_machine_dict(id)
        if data is None:
            return None
        c = Machine()
        c.__dict__.update(data)
        Machine.machine_by_id[data['_id']] = c
        Machine.machine_by_name[data['name']] = c
        return c

    def get_equipment_type(self):
        """Return the equipment type of this machine.
        Users, owners and trainers are reached through this, as they
        are related to all machine of the same type rather than to a
        specific instance."""
        pass

    def get_maintenance_status(self):
        """Return whether the machine is working, possibly with some detail."""
        pass

    def set_maintenance_status(self, flag, detail):
        """Indicate whether the machine is working."""
        pass

    def user_allowed(self, person):
        """Indicate whether a particular person is allowed to use this machine."""
        pass
