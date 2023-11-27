import datetime
import logging
import random

from django.conf import settings
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
import requests

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db.models import Q
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from userauths.utils import calculate_distance, normalize_phone_number
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser,UserProfile
from .serializers import UserSerializer,UserLoginSerializer,UserProfileEditSerializer,UserProfileSerializer,PasswordResetSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import authentication_classes, permission_classes
from django.contrib.auth.hashers import make_password

class UserViewSet(viewsets.ModelViewSet):


    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


    @action(detail=True, methods=["PATCH"])
    def verify_signup(self, request, pk=None):
        instance = self.get_object()

        if instance.is_active:
            return Response(
                "User is already active.",
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate and send OTP
        otp = instance.generate_otp()
        instance.save()
        instance.send_otp(otp)

        # Check if entered OTP matches the stored OTP
        entered_otp = request.data.get("otp")
        if not instance.verify_otp(entered_otp):
            return Response(
                "Please enter a valid OTP.",
                status=status.HTTP_400_BAD_REQUEST
            )

        # If OTP is verified, activate the user
        instance.activate_user()  # You may have a method for activating users in your model

        # Optionally, create a user profile or perform other actions upon activation
        UserProfile.objects.create(user=instance)

        return Response(
            "Successfully verified the user.",
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["PATCH"])
    def regenerate_otp(self, request,pk=None):

        instance = self.get_object()
        if int(instance.max_otp_try) == 0 and timezone.now() < instance.otp_max_out:
            return Response(
                "Max OTP try reached, try after an hour",
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp = random.randint(1000, 9999)
        otp_expiry = timezone.now() + datetime.timedelta(minutes=10)
        max_otp_try = int(instance.max_otp_try) - 1

        instance.otp = otp
        instance.otp_expiry = otp_expiry
        instance.max_otp_try = max_otp_try
        if max_otp_try == 0:
            otp_max_out = timezone.now() + datetime.timedelta(hours=1)
            instance.otp_max_out = otp_max_out
        elif max_otp_try == -1:
            instance.max_otp_try = settings.MAX_OTP_TRY
        else:
            instance.otp_max_out = None
            instance.max_otp_try = max_otp_try
        instance.save()
        instance.sent_otp()
        return Response("Successfully generate new OTP.", status=status.HTTP_200_OK)

    @action(detail=False, methods=["POST"])
    @authentication_classes([IsAuthenticated])
    def login(self, request, pk=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


    @action(detail=False, methods=["POST"])
    @authentication_classes([IsAuthenticated])
    def logout(self, request,pk=None):

        return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["POST"])
    @permission_classes([AllowAny])
    def signup(self, request, pk=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"detail": "User registered successfully."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    Games = [
        ("valorant", "Valorant"),
        ("csgo", "Csgo"),
        ("pubg", "Pubg"),
    ]

    def update_game_choices(self, games):
            if games:
                if games not in dict(self.Games).keys():
                    games_choices = list(self.Games)
                    games_choices.append((games, games))
                    self.Games = tuple(games_choices)

    @action(detail=False, methods=["PUT"])
    @authentication_classes([IsAuthenticated])
    def edit_profile(self, request):
        user = request.user
        serializer = UserProfileEditSerializer(user.profile, data=request.data, partial=True)
        if serializer.is_valid():
            games = request.data.get('games')
            self.update_game_choices(games)
            serializer.save()
            return Response({"detail": "Profile edited successfully."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["GET"])
    @authentication_classes([IsAuthenticated])
    def suggest_profiles(self, request):

        user_profile = request.user.profile
        state = user_profile.state
        country = user_profile.country
        games = user_profile.games

        # Query profiles from the same state
        same_state_profiles = UserProfile.objects.filter(
            Q(state=state) | Q(country=country)
        ).exclude(user=request.user)


        if not same_state_profiles.exists():
            other_state_profiles = UserProfile.objects.filter(
                ~Q(state=state)
            ).exclude(user=request.user)


            serialized_profiles = UserProfileSerializer(other_state_profiles, many=True)
            return Response(serialized_profiles.data)


        serialized_profiles = UserProfileSerializer(same_state_profiles, many=True)
        return Response(serialized_profiles.data)

    @action(detail=False, methods=["POST"])
    @permission_classes([AllowAny])
    def reset_password(self,request):
        if request.method == 'POST':
            phone_number = request.data.get('phone_number')  # Assuming the phone number is sent in the POST request
            normalized_phone_number = normalize_phone_number(phone_number)
            if not normalized_phone_number:
                return Response("Invalid phone number format", status=400)
            try:
                # Validate if the phone number exists in your CustomUser model
                user_instance = get_object_or_404(
                    CustomUser, phone_number=normalized_phone_number)
            except CustomUser.DoesNotExist:
                return Response("User with this phone number does not exist", status=400)
            user_instance.generate_otp()
            otp=user_instance.otp
            user_instance.send_otp(otp)

            return Response("OTP sent successfully")
        else:
            return Response("Invalid request method", status=405)



    @action(detail=False, methods=["PATCH"])
    @permission_classes([AllowAny])
    def set_new_password(self, request):
        phone_number = request.data.get('phone_number')
        entered_otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        try:
            user_instance = CustomUser.objects.get(phone_number=phone_number)
            if user_instance.reset_user_password_with_otp(new_password, entered_otp):
                return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to reset password"}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"error": "User with this phone number does not exist"}, status=status.HTTP_400_BAD_REQUEST)
