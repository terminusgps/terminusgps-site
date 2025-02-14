from django.db.models.signals import post_save
from django.dispatch import receiver

from terminusgps_tracker.models import TrackerProfile
from terminusgps_tracker.models.subscriptions import TrackerSubscription


@receiver(post_save, sender=TrackerProfile)
def create_subscription(sender, instance, created, *args, **kwargs):
    if created:
        TrackerSubscription.objects.create(profile=instance)
