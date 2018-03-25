
class Equipment_class(0bject):

    def __init__(self, identification):
        pass

    def get_machines(self):
        pass

    def get_people(self, role):
        pass

    def get_trained_users(self):
        return self.get_people('trained')

    def get_owners(self):
        return self.get_people('owners')

    def get_trainers(self):
        trainers = self.get_people('trainers')
        if trainers is None or len(trainers) == 0:
            trainers = self.get_owners()
        return trainers

    def request_training(self, person):
        pass
