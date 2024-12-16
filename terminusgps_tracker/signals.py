from django.db.models.signals import post_save
from django.dispatch import receiver

from terminusgps_tracker.models import TrackerSubscription

from .models import TrackerProfile


@receiver(post_save, sender=TrackerProfile)
def create_profile_objects(
    instance: TrackerProfile,
    created: bool,
    raw: bool,
    using: str,
    update_fields: dict | None = None,
) -> None:
    if created:
        TrackerSubscription.objects.create(profile=instance, tier=None)
