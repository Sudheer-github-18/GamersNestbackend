import os
import random
import secrets
import uuid
from dotenv import load_dotenv
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.utils.text import slugify
import requests
from django.contrib.auth.hashers import make_password
from twilio.rest import Client
from shortuuid.django_fields import ShortUUIDField
import shortuuid
from django.dispatch import receiver
from django.db import transaction
from autoslug import AutoSlugField


phone_regex = RegexValidator(
    regex=r"^\+91?\d{10}$", message="Phone number must be 10 digits only."
)



def user_directory_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (instance.user.id, ext)
    return 'user_{0}/{1}'.format(instance.user.id,filename)


class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Users must have a phone_number")
        if password:
            extra_fields['password'] = make_password(password)

        user = self.model(phone_number=phone_number, **extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(phone_number, password=password, **extra_fields)




class CustomUser(AbstractBaseUser,PermissionsMixin):
    username=None

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(
        unique=True, max_length=15, null=True, blank=True, validators=[phone_regex]
    )
    discord_auth_key = models.CharField(max_length=255, blank=True, null=True)
    social_auth_key = models.CharField(max_length=255, blank=True, null=True, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    name = models.CharField(max_length=200,null=True,blank=True)
    dob = models.DateField(max_length=200, null=True, blank=True)
    otp = models.CharField(max_length=6, null=True)
    max_otp_try = models.IntegerField(default=10)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    otp_attempts = models.PositiveSmallIntegerField(default=0)
    last_otp_attempt = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    user_registered_at = models.DateTimeField(default=timezone.now)


    USERNAME_FIELD = 'phone_number'

    objects = UserManager()

    def reset_user_password_with_otp(self, new_password,entered_otp):
        if self.verify_otp(entered_otp):
            try:
                self.set_password(new_password)
                self.save()
                return True
            except Exception as e:
                # Log the exception or handle the error as per your application's requirements
                return False  # Indicates a failed password reset
        return False  # Indicates OTP verification failure

    def activate_user_with_social_key(self, *args, **kwargs):
        if self.social_auth_key or self.discord_auth_key:
            self.is_active = True
            self.save()


    load_dotenv()
    def send_otp(self, otp):
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')



        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_=os.getenv('TWILIO_PHONE_NUMBER'),
            body=f"Your OTP is: {otp}",
            to=self.phone_number
        )

        print(message.sid) # For debugging purposes



    def generate_otp(self):
        if self.last_otp_attempt != timezone.now().date():
            self.otp_attempts = 0  # Reset attempts for a new day

        if self.otp_attempts >= settings.MAX_OTP_TRY:
            return None  # Return None if the limit is reached

        self.otp_attempts += 1
        self.otp = str(secrets.randbelow(1000000)).zfill(6)
        self.otp_expiry = timezone.now() + timezone.timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
        self.save()
        return self.otp


    def verify_otp(self, entered_otp):
        try:
            print(f"Entered OTP: {entered_otp}")
            print(f"Stored OTP: {self.otp}")
            print(f"OTP Expiry: {self.otp_expiry}")
            if (
                self.otp == entered_otp
                and self.otp_expiry
                and timezone.now() < self.otp_expiry
            ):
                print("OTP verification succeeded.")
                return True
            else:
                print("OTP verification failed.")
        except AttributeError as attr_error:
            print(f"AttributeError occurred: {attr_error}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        return False

    def activate_user(self):
        self.is_active = True
        self.otp_expiry = timezone.now()
        self.otp_attempts = 0
        self.save()

    def save(self, *args, **kwargs):
        # Ensure the phone number includes the country code before saving
        if self.phone_number and not self.phone_number.startswith('+'):
            # Assuming the country code for India is '+91'
            # Replace '+91' with your country code
            self.phone_number = f'+91{self.phone_number}'

        if not self.id:  # Generate id only if it doesn't exist and name is not None
            name_to_id = self.name.replace(
                ' ', '_') if self.name else 'default_name'
            unique_id = f"{name_to_id}_{uuid.uuid4().hex[:6]}"
            self.id = unique_id

        if not self.slug:
            self.slug = f"{str(self.id)}" if self.name else f"user-{str(self.id)}"

        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.phone_number) and str(self.id)

def generate_pid():
    return shortuuid.ShortUUID().random(length=7)

class UserProfile(models.Model):
    pid = models.CharField(
        max_length=25,
        default=generate_pid,
        unique=True,
        primary_key=True
    )
    user = models.OneToOneField(
        CustomUser,
        related_name="profile",
        on_delete=models.CASCADE,
        unique=True
    )
    Games = (
        ("valorant", "Valorant"),
        ("csgo", "Csgo"),
        ("pubg", "Pubg")
    )

    Gender=(
        ("male","Male"),
        ("female","Female"),
        ("other","Other")
    )

    gamer_name=models.CharField(max_length=200,unique=True,blank=False)
    games=models.CharField(max_length=100,choices=Games,null=True,blank=True)
    image = models.ImageField(upload_to=user_directory_path, default="default.jpg", null=True,blank=True)
    email=models.EmailField(max_length=100,null=True,blank=True)
    full_name = models.CharField(max_length=50, null=True, blank=True)
    gender=models.CharField(max_length=200,choices=Gender,default='male')
    phone_number = models.CharField(max_length=20,blank=True,unique=True)
    friends = models.ManyToManyField(CustomUser, blank=True, related_name="user_friends")
    blocked = models.ManyToManyField(CustomUser, blank=True, related_name="blocked")
    date = models.DateTimeField(default=timezone.now)
    slug=models.SlugField(unique=True, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)


    def save(self, *args, **kwargs):
        if not self.slug or self.slug == "":
            uuid_key = shortuuid.uuid()
            unique_id = uuid_key[:2]
            self.slug = slugify(self.gamer_name) + '-' + str(unique_id.lower())
        super().save(*args, **kwargs)


    @receiver(post_save, sender=CustomUser)
    def create_profile_on_activation(sender, instance, created, **kwargs):
        if created and instance.is_active:
            UserProfile.objects.create(user=instance)

    def __str__(self):
        try:
            return str(self.gamer_name or self.phone_number or self.pid) or 'Default String'
        except Exception as e:
            print(f"Error in __str__ method: {e}")
            print(f"Instance: {self.__dict__}")
            print(f"Full Name: {self.full_name}")
            print(f"Phone Number: {self.phone_number}")
            print(f"PID: {self.pid}")
            print(f"User: {self.user}")
            return f"Error in __str__ method: {e}"



