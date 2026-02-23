from django.core.management.base import BaseCommand
from users.models import User
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

class Command(BaseCommand):
    help = "Reset JWT tokens and optionally delete test users"

    def handle(self, *args, **kwargs):
        # Delete all blacklisted tokens first
        BlacklistedToken.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("✅ Deleted all BlacklistedTokens"))

        # Delete all outstanding tokens
        OutstandingToken.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("✅ Deleted all OutstandingTokens"))

        # Delete specific test users by email/username
        test_users = User.objects.filter(email="test@test.com")
        if test_users.exists():
            count = test_users.count()
            test_users.delete()
            self.stdout.write(self.style.SUCCESS(f"✅ Deleted {count} test user(s)"))

        # Optional: recreate a fresh test user
        u = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="test1234"
        )
        self.stdout.write(self.style.SUCCESS(f"✅ Created fresh test user: {u.username}"))