from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from .models import OTPCode

@receiver(post_save, sender=OTPCode)
def delete_old_otps(sender, instance, **kwargs):
    expire_time = timezone.now() - timedelta(minutes=1)
    OTPCode.objects.filter(created_at__lt=expire_time).delete()