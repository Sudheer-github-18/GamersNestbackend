from django.db import models
from userauths.models import CustomUser
from django.core.exceptions import ValidationError
# Create your models here.

class Friend(models.Model):
    user1 = models.ForeignKey(CustomUser, related_name='user1_friends', on_delete=models.CASCADE)
    user2 = models.ForeignKey(CustomUser, related_name='user2_friends', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user1} <-> {self.user2}"

class FriendRequest(models.Model):
    from_user = models.ForeignKey(CustomUser, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name='received_requests', on_delete=models.CASCADE)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def clean(self):
        # Prevent self-sending of friend requests
        if self.from_user == self.to_user:
            raise ValidationError("Cannot send friend request to yourself.")

    def save(self, *args, **kwargs):
        # If the friend request is accepted, create a friendship
        if self.status == 'accepted':
            Friend.objects.create(user1=self.from_user, user2=self.to_user)
            Friend.objects.create(user1=self.to_user, user2=self.from_user)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.from_user} -> {self.to_user}: {self.status}"


class Tournament(models.Model):
    GAME_CHOICES = (
        ('valorant', 'Valorant'),
        ('pubg_mobile', 'PUBG Mobile'),
        ('csgo', 'CsGo')
    )

    name = models.CharField(max_length=100)
    game_type = models.CharField(max_length=20, choices=GAME_CHOICES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    entry_fee = models.DecimalField(max_digits=6, decimal_places=2)
    participants = models.ManyToManyField(CustomUser, related_name='tournaments_participating')
    teams = models.ManyToManyField(CustomUser, related_name='tournaments_teams')
    winning_team = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='tournaments_won')
    removed_player = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='tournaments_removed')
    added_player = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='tournaments_added')

    def __str__(self):
        return self.name