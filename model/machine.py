import database
import datetime
import person

class Machine(object):

    machine_by_id = {}
    machine_by_name = {}

    def __init__(self, name, equipment_type):
        """Set up a machine's data, from its name."""
        self.name = name
        self.equipment_type = equipment_type
        self.status = 'unknown'
        self.status_detail = None
        self.maintenance_history = []
        self.maintenance_due = None
        self.Location = None
        self.brand = None
        self.model = None
        self.serial_number = None
        self.acquired = None
        self.reservations = []

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

    def save(self):
        """Save the machine to the database."""
        database.save_machine(self.__dict__)

    def get_status(self):
        """Return whether the machine is working, possibly with some detail."""
        return (self.status, self.status_detail)

    def set_status(self, flag, detail):
        """Indicate whether the machine is working."""
        self.status = flag
        self.status_detail = detail
        self.save()

    def reserve(starting_at, ending_at, for_whom, reason):
        """Reserve the machine (e.g. for a training session)."""
        self.reservations = sorted(self.reservations + [[starting_at, ending_at, for_whom, reason]], lambda res: res[0])
        self.save()

    def reserved(when=datetime.datetime.now()):
        """Return whether the machine is reserved (e.g. for a training session).
        The result is a description of the reservation."""
        for res in self.reservations:
            if res[0] < when and res[1] > when:
                return res
        return None

    def user_allowed(self, who):
        """Indicate whether a particular person is allowed to use this machine."""
        res = self.reserved()
        person_obj = person.Person.find(who)
        if res:
            return person_obj._id == res[2]
        return person_obj.qualification(self.name)

    def log_use(self, who, when=datetime.datetime.now()):
        """Log that a particular user has used this machine."""
        database.log_machine_use(self._id, person.Person.find(who)._id, when)

    def get_log(self):
        return database.get_machine_log(self._id)
    
