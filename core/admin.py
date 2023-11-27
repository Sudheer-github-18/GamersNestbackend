from django.contrib import admin
from .models import FriendRequest,Friend,Tournament


class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'status')
    list_filter = ('status',)
    search_fields = ('from_user__username', 'to_user__username')

class FriendAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2')
    search_fields = ('user1__username', 'user2__username')

class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'game_type', 'start_date', 'end_date', 'entry_fee')
    list_filter = ('game_type', 'start_date', 'end_date')
    search_fields = ('name', 'game_type')
    filter_horizontal = ('participants', 'teams')


admin.site.register(FriendRequest, FriendRequestAdmin)
admin.site.register(Friend, FriendAdmin)
admin.site.register(Tournament, TournamentAdmin)