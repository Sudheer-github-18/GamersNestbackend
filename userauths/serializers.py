from datetime import datetime, timedelta
import random
from django.conf import settings
from rest_framework import serializers

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser,UserProfile
from django.utils.translation import gettext_lazy as _



class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(
        write_only=True,
        min_length=settings.MIN_PASSWORD_LENGTH,
        error_messages={
            "min_length": "Password must be longer than {} characters".format(
                settings.MIN_PASSWORD_LENGTH
            )
        },
    )
    password2 = serializers.CharField(
        write_only=True,
        min_length=settings.MIN_PASSWORD_LENGTH,
        error_messages={
            "min_length": "Password must be longer than {} characters".format(
                settings.MIN_PASSWORD_LENGTH
            )
        },
    )
    class Meta:
        model = CustomUser
        fields = (
            "id",
            "phone_number",
            "password1",
            "password2"

        )
        read_only_fields = ("id",)




    def create(self, validated_data):

        otp = random.randint(1000, 9999)
        otp_expiry = datetime.now() + timedelta(minutes = 10)

        user = CustomUser(
            phone_number=validated_data["phone_number"],
            otp=otp,
            otp_expiry=otp_expiry,
            max_otp_try=settings.MAX_OTP_TRY
        )
        user.set_password(validated_data["password1"])
        user.save()
        user.send_otp(validated_data["phone_number"], otp)
        return user

class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    def validate(self, data):
        phone_number = data.get('phone_number')
        password = data.get('password')

        user = authenticate(request=self.context.get('request'), username=phone_number, password=password)

        if not user:
            raise serializers.ValidationError(_("Invalid credentials or user is not active."))

        if not user.is_active:
            raise serializers.ValidationError(_("User is not active."))

        refresh = RefreshToken.for_user(user)
        data['token'] = str(refresh.access_token)
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['image', 'full_name', 'phone_number', 'friends', 'blocked', 'games']


class UserProfileEditSerializer(serializers.ModelSerializer):

    games = serializers.CharField(max_length=100, allow_blank=True, required=False)
    class Meta:
        model = UserProfile
        fields = ['image', 'full_name',  'games' , 'state', 'country']

    def update(self, instance, validated_data):

        games = validated_data.get('games', None)

        instance.image = validated_data.get('image', instance.image)
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.state = validated_data.get('state', instance.state)
        instance.country = validated_data.get('country', instance.country)


        instance.games = games if games is not None else ""
        instance.save()


        return instance

class PasswordResetSerializer(serializers.ModelSerializer):
    phone_number=serializers.CharField()
    new_password = serializers.CharField(write_only=True)


