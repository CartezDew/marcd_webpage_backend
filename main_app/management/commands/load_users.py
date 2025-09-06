from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import json
import os

class Command(BaseCommand):
    help = 'Load users from users.json into the database'

    def handle(self, *args, **options):
        # Get the path to users.json
        users_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', 'users.json')
        users_file = os.path.abspath(users_file)
        
        if not os.path.exists(users_file):
            self.stdout.write(self.style.ERROR(f'Users file not found at {users_file}'))
            return

        # Load users from JSON
        with open(users_file, 'r') as f:
            users_data = json.load(f)

        created_count = 0
        updated_count = 0

        for user_data in users_data:
            username = user_data['fields']['username']
            email = user_data['fields']['email']
            password = user_data['fields']['password']
            is_superuser = user_data['fields']['is_superuser']
            is_staff = user_data['fields']['is_staff']
            is_active = user_data['fields']['is_active']
            first_name = user_data['fields']['first_name']
            last_name = user_data['fields']['last_name']
            date_joined = user_data['fields']['date_joined']

            # Check if user already exists
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_superuser': is_superuser,
                    'is_staff': is_staff,
                    'is_active': is_active,
                    'date_joined': date_joined,
                }
            )

            if created:
                # Set the password for new users
                user.set_password('test123')  # Set a default password
                user.save()
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
            else:
                # Update existing user
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                user.is_superuser = is_superuser
                user.is_staff = is_staff
                user.is_active = is_active
                user.save()
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'Updated user: {username}'))

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {len(users_data)} users. '
                f'Created: {created_count}, Updated: {updated_count}'
            )
        )
