from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class SocialAuthBackend(ModelBackend):
    def authenticate(self, request, social_auth_key=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(social_auth_key=social_auth_key)
        except UserModel.DoesNotExist:
            return None

        return user if self.user_can_authenticate(user) else None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
