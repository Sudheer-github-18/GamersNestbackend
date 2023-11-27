from django.contrib import admin
from .models import CustomUser
from .models import UserProfile
# Register your models here.

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'phone_number', 'image', 'games', ]



admin.site.register(CustomUser)
admin.site.register(UserProfile,ProfileAdmin)