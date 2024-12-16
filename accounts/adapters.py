from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from accounts.models import Account, UserProfile

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Handle social users: Link or create accounts as needed.
        """
        if not sociallogin.user.email:
            return  # Cannot proceed without an email.

        email = sociallogin.user.email

        try:
            user = Account.objects.get(email=email)
            sociallogin.user = user  # Link to existing user.
        except Account.DoesNotExist:
            # If the user doesn't exist, create a new one.
            user = self.create_user_from_sociallogin(sociallogin)
            sociallogin.user = user

    def create_user_from_sociallogin(self, sociallogin):
        """
        Create a new user from social login data.
        """
        user = Account(
            email=sociallogin.user.email,
            username=self.generate_unique_username(sociallogin.user.email.split('@')[0]),
            password=None,
            first_name=sociallogin.user.first_name or '',
            last_name=sociallogin.user.last_name or '',
            is_active=True,
        )
        user.set_unusable_password()
        user.save()

        # Create a profile for additional data storage.
        UserProfile.objects.create(
            user=user,
            additional_data=sociallogin.account.extra_data,  # Almacenar aquí los datos adicionales
        )

        # Automatically mark the email as verified.
        EmailAddress.objects.create(
            user=user,
            email=user.email,
            verified=True,
            primary=True,
        )
        return user


    def generate_unique_username(self, base_username):
        """
        Generate a unique username.
        """
        counter = 1
        username = base_username
        while Account.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        return username


class MyAccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter for manual user registrations.
    """
    pass
