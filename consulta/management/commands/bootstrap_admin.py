from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = (
        "Creates or updates a superuser using environment variables: "
        "DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD."
    )

    def add_arguments(self, parser):
        parser.add_argument('--username', help='Override username (fallback to env)')
        parser.add_argument('--email', help='Override email (fallback to env)')
        parser.add_argument('--password', help='Override password (fallback to env)')

    def handle(self, *args, **options):
        User = get_user_model()
        username = options.get('username') or os.getenv('DJANGO_SUPERUSER_USERNAME')
        email = options.get('email') or os.getenv('DJANGO_SUPERUSER_EMAIL')
        password = options.get('password') or os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if not username or not password:
            self.stderr.write(
                self.style.ERROR(
                    'username and password are required. Provide via args or env variables.'
                )
            )
            return 1

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email or ''}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created user '{username}'"))
        else:
            self.stdout.write(self.style.WARNING(f"User '{username}' already exists, updating..."))

        if email and user.email != email:
            user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        self.stdout.write(self.style.SUCCESS('Superuser ensured/updated successfully.'))
