from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from makespace_training_system.training_system.models import EquipmentType, Equipment
from makespace_training_system.users.models import User


class Command(BaseCommand):
    help = 'Loads test data for development'

    def handle(self, *args, **options):
        # Create superuser
        um = get_user_model()
        um.objects.create_superuser('djadmin', 'djadmin@demo.makespace.org', 'testtest')

        # Load new users
        for u_name in ["user", "trainer", "owner", "admin", "auditor"]:
            u = User()
            u.username = u_name
            u.email = "%s@demo.makespace.org" % u_name
            u.set_password('testtest')
            u.save()

        # Load Equipment
        et = EquipmentType()
        et.name = 'Laser Cutter'
        et.category = 'R'
        et.save()

        for e_name in ['Betsy', 'Jaws']:
            e = Equipment()
            e.name = e_name
            e.equipment_type = et
            e.save()

        self.stdout.write(self.style.SUCCESS('Successfully loaded test data'))
