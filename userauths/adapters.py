from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user
        user.social_auth_key = sociallogin.account.uid
        user.discord_auth_key = sociallogin.account.extra_data.get('code')
        if user.social_auth_key or user.discord_auth_key:
            user.activate_user_with_social_key([user.social_auth_key, user.discord_auth_key])
        user.save()


