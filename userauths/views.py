import datetime
import logging
import random
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
import requests
from rest_framework.views import APIView
from userauths.backends import SocialAuthBackend
from .utils import custom_response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from django.db.models import Q
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from userauths.utils import  normalize_phone_number
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import CustomUser, UserProfile
from .serializers import UserProfileUpdateSerializer, UserSerializer, UserLoginSerializer, UserProfileEditSerializer, UserProfileSerializer, YourFacebookTokenSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import authentication_classes, permission_classes
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.views import TokenObtainPairView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter


class UserDetailView(RetrieveAPIView):
    queryset = CustomUser.objects.all()  # Replace 'User' with your actual model
    serializer_class = UserSerializer  # Replace with your serializer

    # Optionally, you can override the get_object method to retrieve the user based on UUID
    def get_object(self):
        # Get the UUID from the URL kwargs
        uuid = self.kwargs.get('pk')

        # Get the user based on the UUID
        user = self.queryset.filter(pk=uuid).first()
        return user


class UserViewSet(viewsets.ModelViewSet):

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


    @action(detail=True, methods=["PATCH"])
    def verify_signup(self, request, pk=None):
        instance = self.get_object()
        user_data = {
            "user_id": instance.id,

            # Include any other relevant user information
        }

        if instance.is_active:
            return custom_response(
                False, data=user_data, message="user is already active"
            )

        # Check if entered OTP matches the stored OTP
        entered_otp = request.data.get("otp")
        if not instance.verify_otp(entered_otp):
            return custom_response(
                False, data=user_data, message="enter the correct otp "
            )

        # If OTP is verified, activate the user
        instance.activate_user()  # You may have a method for activating users in your model
        user_profile, created = UserProfile.objects.get_or_create(
            user=instance)
        # Optionally, create a user profile or perform other actions upon activation
        phone_number = request.data.get("phone_number")
        if phone_number:
            user_profile.phone_number = phone_number
            user_profile.save()
        elif instance.phone_number:
            user_profile.phone_number = instance.phone_number
            user_profile.save()

        return custom_response(
            True, data=user_data, message="User is verified"
        )



    @action(detail=False, methods=["POST"])
    @authentication_classes([IsAuthenticated])
    def login(self, request, pk=None):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            phone_number = serializer.validated_data.get('phone_number')
            token = serializer.validated_data.get('token')
            if phone_number and token:
            # If necessary fields are present, construct the success response
                response_data = {

                    "token with phonenumber": {
                        "phone_number": phone_number,
                        "token": token,
                        # Add more user-related data if necessary
                    },

                }
                return custom_response(True, data=response_data, message="User is verified")
            else:
                # If the necessary fields are not present, construct an error response
                return custom_response(False, data={"non_field_errors": ["Invalid credentials or user is not active."]}, message="Invalid credentials or user is not active.")
        else:
            # If serializer is not valid, construct error response
            return custom_response(False, data=serializer.errors, message="Invalid input data.")

    @action(detail=False, methods=["POST"])
    def social_login(self, request, pk=None):
        social_auth_key = request.data.get('social_auth_key')
        user = SocialAuthBackend().authenticate(request, social_auth_key=social_auth_key)

        if user:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            response_data = {
                "user_id": user.id,
                "token": access_token,
                # Add more user-related data if necessary
            }

            return custom_response(True, data=response_data, message="User is verified")
        else:
            return custom_response(False, data={"non_field_errors": ["Invalid credentials or user is not active."]}, message="Invalid credentials or user is not active.")

    @action(detail=False, methods=["POST"])
    @authentication_classes([IsAuthenticated])
    def logout(self, request, pk=None):

        return custom_response(True, data=None, message="User is verified")

    @action(detail=False, methods=["POST"])
    @permission_classes([AllowAny])
    def signup(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response_data = {
                "user_id": user.id,
                "phone_number":user.phone_number,
            }
            return custom_response(True, data=response_data, message="User registered successfully.")
        else:
            return custom_response(False, data=serializer.errors, message="Failed to register user")

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
        profile_instance = getattr(user, 'profile', None)
        if request.data:  # Check if request body exists
            if profile_instance:
                serializer = UserProfileEditSerializer(profile_instance, data=request.data, partial=True)
                if serializer.is_valid():
                    games = request.data.get('games')
                    profile_instance.games = games  # Update games field in UserProfile
                    serializer.save()
                    response_data = {  # Corrected dictionary structure

                        "data": "Profile edited successfully."
                        ,

                    }
                    return custom_response(True, data=response_data)
                else:
                    return custom_response(False, data=serializer.errors)
            else:
                return custom_response(False, data={"detail": "Profile does not exist."})
        else:  # If no request body, return editable fields
            if profile_instance:
                editable_fields = {
                    "editable_fields": {
                        # Include other editable fields here
                        "games": profile_instance.games,
                        "image_url": profile_instance.image.url,
                        "full_name": profile_instance.full_name,
                        "state": profile_instance.state,
                        "country": profile_instance.country
                    }
                }
                return custom_response(False, data=editable_fields, message="Editable fields available")
            else:
                return custom_response(False, data=None, message="Profile does not exist")

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

            serialized_profiles = UserProfileSerializer(
                other_state_profiles, many=True)
            return Response(serialized_profiles.data)

        serialized_profiles = UserProfileSerializer(
            same_state_profiles, many=True)
        return Response(serialized_profiles.data)

    @action(detail=False, methods=["POST"])
    @permission_classes([AllowAny])
    def reset_password(self, request):
        if request.method == 'POST':
            # Assuming the phone number is sent in the POST request
            phone_number = request.data.get('phone_number')
            normalized_phone_number = normalize_phone_number(phone_number)
            if not normalized_phone_number:
                return custom_response(False, data=None, message="enter correct phonenumber")
            response_data = {

            }
            try:
                # Validate if the phone number exists in your CustomUser model
                user_instance = get_object_or_404(
                    CustomUser, phone_number=normalized_phone_number)
                user_instance.generate_otp()
                otp = user_instance.otp
                user_instance.send_otp(otp)
                response_data = {"otp": otp}  # Assign response data for successful user found
                return custom_response(True, data=response_data, message="OTP sent successfully")

            except CustomUser.DoesNotExist:
                return custom_response(False, data=response_data, message="User does not exist")

        return custom_response(False, data=None, message="Invalid request")





    @action(detail=False, methods=["PATCH"])
    @permission_classes([AllowAny])
    def set_new_password(self, request):
        phone_number = request.data.get('phone_number')
        entered_otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        try:
            user_instance = CustomUser.objects.get(phone_number=phone_number,)
            if user_instance.reset_user_password_with_otp(new_password, entered_otp):
                return custom_response(True,
                                message="Password Reset Successfull")
            else:
                return custom_response(False, data=None,
                                       message="Password Reset UnSuccessfull")
        except CustomUser.DoesNotExist:
            return custom_response(False, data=None,
                                   message="user with this phonenumber doesnt exist")

class ProfileUpdateView(APIView):
    def put(self, request, *args, **kwargs):
        user_profile = UserProfile.objects.get(user=request.user)  # Assuming user is authenticated

        serializer = UserProfileUpdateSerializer(user_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ObtainTokenPairWithFacebook(TokenObtainPairView):
    serializer_class = YourFacebookTokenSerializer
     # Replace with your serializer







