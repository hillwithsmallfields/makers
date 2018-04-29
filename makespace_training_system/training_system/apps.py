from django.apps import AppConfig


class TrainingSystemConfig(AppConfig):
    name = 'makespace_training_system.training_system'

    verbose_name = "Training System"

    def ready(self):
        pass
