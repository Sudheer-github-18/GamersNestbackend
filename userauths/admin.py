from django.contrib import admin
from .models import CustomUser
from .models import UserProfile
# Register your models here.



class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'pid', 'phone_number', 'image', 'games', ]
    def image_display(self, obj):
        if obj.image:
            return '<img src="{}" width="50px" height="50px" />'.format(obj.image.url)
        else:
            return 'No Image'
    image_display.allow_tags = True

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('slug','id','phone_number','user_registered_at','name')



admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(UserProfile,UserProfileAdmin)