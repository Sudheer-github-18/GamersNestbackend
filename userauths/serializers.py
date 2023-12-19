from datetime import datetime, timedelta, timezone

import random
from django.utils import timezone
from django.conf import settings

from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser,UserProfile
from django.utils.translation import gettext_lazy as _



class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=settings.MIN_PASSWORD_LENGTH,
        error_messages={
            "min_length": "Password must be longer than {} characters".format(
                settings.MIN_PASSWORD_LENGTH
            )
        },)



    phone_number=serializers.CharField(
        error_messages={
            "phone":"add a phone number with your country code "
        }
    )


    class Meta:
        model = CustomUser
        fields = (
            "id",
            "phone_number",
            "password",



        )
        read_only_fields = ("id",)

    def create(self, validated_data):
        # Separate the password from validated_data
        password = validated_data.pop('password', None)

        # Create the user object without the password
        user = CustomUser.objects.create(**validated_data)

        # If a password was provided, set it for the user
        if password:
            user.set_password(password)
            user.save()

        # Generate OTP and handle its expiry and other attributes
        otp = user.generate_otp()
        otp_expiry = timezone.now() + timedelta(minutes=10)
        user.otp = otp
        user.otp_expiry = otp_expiry
        user.max_otp_try = settings.MAX_OTP_TRY
        user.save()

        # Send OTP (if send_otp() is a method of CustomUser)
        user.send_otp(otp)

        return user


class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    def validate(self, data):
        phone_number = data.get('phone_number')
        password = data.get('password')

        user = authenticate(request=self.context.get('request'), phone_number=phone_number, password=password)

        if not user:
            raise serializers.ValidationError(_("Invalid credentials or user is not active."))

        if not user.is_active:
            raise serializers.ValidationError(_("User is not active."))

        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        return {
            'phone_number': phone_number,
            'token': token,
            # Add more fields if needed for your response
        }

class UserProfileSerializer(serializers.ModelSerializer):
    friends = serializers.PrimaryKeyRelatedField(
        many=True, queryset=CustomUser.objects.all())
    blocked = serializers.PrimaryKeyRelatedField(
        many=True, queryset=CustomUser.objects.all())

    class Meta:
        model = UserProfile
        fields = ['image', 'full_name', 'phone_number', 'friends', 'blocked', 'games',]


class UserProfileEditSerializer(serializers.ModelSerializer):

    games = serializers.ChoiceField(choices=UserProfile.Games)
    class Meta:
        model = UserProfile
        fields = ['image', 'full_name',  'games' , 'state', 'country']

    def update(self, instance, validated_data):

        games = validated_data.pop('games', None)

        instance.image = validated_data.get('image', instance.image)
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.state = validated_data.get('state', instance.state)
        instance.country = validated_data.get('country', instance.country)

        if games is not None:
            instance.games = games

        instance.save()
        return instance

class PasswordResetSerializer(serializers.ModelSerializer):
    phone_number=serializers.CharField()
    new_password = serializers.CharField(write_only=True)


class YourFacebookTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('full_name', 'gamer_name', 'gender')

    def validate(self, data):
        # Ensure full_name, gamer_name, and gender are provided
        if 'full_name' not in data or 'gamer_name' not in data or 'gender' not in data:
            raise serializers.ValidationError("full_name, gamer_name, and gender are required fields.")
        return data




