from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import date

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    earnings = models.DecimalField(max_digits=12, decimal_places=2, default=100)  # default daily earning
    last_earning_update = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    
    def __str__(self):
        return self.user.username


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
        ('trade', 'Trade'),
        ('reward', 'Reward'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coin = models.CharField(max_length=32)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    tx_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20, default='Completed')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} {self.tx_type} {self.amount} {self.coin}"


# Auto-create Profile when a new user is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

