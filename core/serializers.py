from rest_framework import serializers
from .models import FriendRequest,Friend
from userauths.models import UserProfile

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = '__all__'

class FriendSerializer(serializers.ModelSerializer):
    friends = serializers.SerializerMethodField()

    class Meta:
        model = Friend
        fields = ('friends',)

    def get_friends(self, obj):
        # Check if obj is a single instance or a queryset
        if isinstance(obj, Friend):
            user1_name = getattr(obj.user1, 'profile', None).full_name if obj.user1 else None
            user2_name = getattr(obj.user2, 'profile', None).full_name if obj.user2 else None

            current_user_name = self.context['request'].user.profile.full_name

            return [name for name in [user1_name, user2_name] if name and name != current_user_name]

        # If it's a queryset, loop through and call get_friends for each instance
        return list(set(friend for instance in obj for friend in self.get_friends(instance)))