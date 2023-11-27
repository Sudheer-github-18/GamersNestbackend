from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets,permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from userauths.models import CustomUser
from .models import FriendRequest,Friend
from .serializers import FriendRequestSerializer,FriendSerializer
from django.db.models import Q
from rest_framework.permissions import IsAdminUser
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt

class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["POST"])
    def send_friend_request(self, request):

        sender = request.user
        recipient_id = request.data.get('recipient_id')
        try:
            recipient = CustomUser.objects.get(id=recipient_id)
        except CustomUser.DoesNotExist:
            return Response({"detail": "Recipient not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if a friend request already exists
        existing_request = FriendRequest.objects.filter(from_user=sender, to_user=recipient).first()
        if existing_request:
            return Response({"detail": "Friend request already sent."}, status=status.HTTP_400_BAD_REQUEST)

        # Create and save a new friend request
        friend_request = FriendRequest(from_user=sender, to_user=recipient)
        friend_request.save()

        return Response({"detail": "Friend request sent successfully."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["POST"])
    def accept_friend_request(self, request, pk=None):
        # Get the friend request by its ID
        try:
            friend_request = FriendRequest.objects.get(id=pk)
        except FriendRequest.DoesNotExist:
            return Response({"detail": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the current user is the recipient of the friend request
        if request.user != friend_request.to_user:
            return Response({"detail": "You are not authorized to accept this request."}, status=status.HTTP_401_UNAUTHORIZED)

        # Update the status of the friend request to 'accepted'
        friend_request.status = 'accepted'
        friend_request.save()

        # Add the sender to the recipient's friends list and vice versa
        friend_request.to_user.profile.friends.add(friend_request.from_user)
        friend_request.from_user.profile.friends.add(friend_request.to_user)

        recipient_friends = friend_request.to_user.profile.friends.all()
        sender_friends = friend_request.from_user.profile.friends.all()

        friend_request.to_user.profile.friends.set(recipient_friends)
        friend_request.from_user.profile.friends.set(sender_friends)

        return Response({"detail": "Friend request accepted successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def decline_friend_request(self, request, pk=None):
        # Get the friend request by its ID
        try:
            friend_request = FriendRequest.objects.get(id=pk)
        except FriendRequest.DoesNotExist:
            return Response({"detail": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the current user is the recipient of the friend request
        if request.user != friend_request.to_user:
            return Response({"detail": "You are not authorized to decline this request."}, status=status.HTTP_401_UNAUTHORIZED)

        # Update the status of the friend request to 'declined'
        friend_request.status = 'declined'
        friend_request.save()

        return Response({"detail": "Friend request declined successfully."}, status=status.HTTP_200_OK)

class FriendViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        friend_object = Friend.objects.filter(Q(user1=user) | Q(user2=user))
        return [friend_object]

