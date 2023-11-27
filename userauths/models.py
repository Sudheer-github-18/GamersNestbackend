import random
import secrets
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.utils.text import slugify
import requests
from twilio.rest import Client
from shortuuid.django_fields import ShortUUIDField
import shortuuid
from django.dispatch import receiver
from django.db import transaction


phone_regex = RegexValidator(
    regex=r"^\+91?\d{10}$", message="Phone number must be 10 digits only."
)

Games=(
    ("valorant","Valorant"),
    ("csgo","Csgo"),
    ("pubg","Pubg")
)

def user_directory_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (instance.user.id, ext)
    return 'user_{0}/{1}'.format(instance.user.id,filename)

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None):
        if not phone_number:
            raise ValueError("Users must have a phone_number")
        user = self.model(phone_number=phone_number)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password):
        user = self.create_user(
            phone_number=phone_number, password=password
        )
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser,PermissionsMixin):
    username=None
    phone_number = models.CharField(
        unique=True, max_length=15, null=False, blank=False, validators=[phone_regex]
    )
    name = models.CharField(max_length=200,null=True,blank=True)
    dob = models.DateTimeField(max_length=200, null=True, blank=True)
    otp = models.CharField(max_length=6, null=True)
    max_otp_try = models.IntegerField(default=10)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    otp_attempts = models.PositiveSmallIntegerField(default=0)
    last_otp_attempt = models.DateField(auto_now_add=True, null=True)
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

    def __str__(self):
        return self.phone_number

    def send_otp(self, otp):
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN


        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_=settings.TWILIO_PHONE_NUMBER,
            body=f"Your OTP is: {otp}",
            to=self.phone_number
        )

        print(message.sid)  # For debugging purposes



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
        self.otp_expiry = None
        self.otp_attempts = 0
        self.save()

    def save(self, *args, **kwargs):
        # Ensure the phone number includes the country code before saving
        if not self.phone_number.startswith('+'):
            # Assuming the country code for India is '+91'
            # Replace '+91' with your country code
            self.phone_number = f'+91{self.phone_number}'

        # Additional processing or validation if needed before saving

        super().save(*args, **kwargs)

    def __str__(self):
        return (self.phone_number)

class UserProfile(models.Model):
    pid = ShortUUIDField(length=7, max_length=25, alphabet='abcdefghijklmnopqrstuvwxyz')
    user = models.OneToOneField(
        CustomUser,
        related_name="profile",
        on_delete=models.CASCADE,
        primary_key=True,
    )
    games=models.CharField(max_length=100,choices=Games,null=True,blank=True)
    image = models.ImageField(upload_to=user_directory_path, default="default.jpg", null=True,blank=True)
    full_name = models.CharField(max_length=50, null=False, blank=False)

    phone_number = models.CharField(
        max_length=15, null=False, blank=False, validators=[phone_regex],default=''
    )
    friends = models.ManyToManyField(CustomUser, blank=True, related_name="user_friends")
    blocked = models.ManyToManyField(CustomUser, blank=True, related_name="blocked")
    date = models.DateTimeField(default=timezone.now)
    slug=models.SlugField(unique=True, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        if self.full_name:
            return self.full_name
        elif self.user and hasattr(self.user, 'pid'):
            return self.user.pid
        else:
            return str(self.user)

    def save(self,*args,**kwargs):
        if self.slug == "" or self.slug == None:
            uuid_key= shortuuid.uuid()
            uniqueid = uuid_key[:2]
            self.slug = slugify(self.full_name) + '-' + str(uniqueid.lower())
        super(UserProfile,self).save(*args,**kwargs)


@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created and not settings.DEBUG:
        with transaction.atomic():
            if not hasattr(instance, 'profile'):
                profile = UserProfile.objects.create(
                    user=instance,
                    phone_number=instance.phone_number
                )
            else:
                profile = instance.profile
                profile.phone_number = instance.phone_number
                profile.save()



