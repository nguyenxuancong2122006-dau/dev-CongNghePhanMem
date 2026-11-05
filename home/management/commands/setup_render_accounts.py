import os

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Create Cong Store admin, employee, and manager accounts"

    def handle(self, *args, **options):
        User = get_user_model()

        accounts = [
            {
                "username": os.environ.get(
                    "ADMIN_USERNAME",
                    "nguyenxuancong2122006@gmail.com",
                ),
                "password": os.environ.get("ADMIN_PASSWORD"),
                "role": "Admin",
                "superuser": True,
            },
            {
                "username": os.environ.get(
                    "EMPLOYEE_USERNAME",
                    "employee@congstore.local",
                ),
                "password": os.environ.get("EMPLOYEE_PASSWORD"),
                "role": "Employee",
                "superuser": False,
            },
            {
                "username": os.environ.get(
                    "MANAGER_USERNAME",
                    "manager@congstore.local",
                ),
                "password": os.environ.get("MANAGER_PASSWORD"),
                "role": "Manager",
                "superuser": False,
            },
        ]

        for account in accounts:
            username = account["username"]
            password = account["password"]

            if not username or not password:
                raise CommandError(
                    f"Missing username or password for {account['role']}"
                )

            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": username},
            )

            user.email = username
            user.is_active = True
            user.is_staff = True
            user.is_superuser = account["superuser"]
            user.set_password(password)
            user.save()

            group, _ = Group.objects.get_or_create(name=account["role"])
            user.groups.set([group])

            self.stdout.write(
                self.style.SUCCESS(
                    f"{account['role']} account ready: {username}"
                )
            )