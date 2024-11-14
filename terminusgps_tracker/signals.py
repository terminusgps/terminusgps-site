from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from terminusgps_tracker.models import TrackerProfile


@receiver(post_save, sender=get_user_model())
def create_tracker_profile(sender, instance, created, **kwargs) -> None:
    if created:
        TrackerProfile.objects.create(user=instance)
