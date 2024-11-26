from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from terminusgps_tracker.models import (
    TodoItem,
    TrackerProfile,
    TrackerShippingAddress,
    TrackerSubscription,
    TrackerTodoList,
)


@receiver(post_save, sender=get_user_model())
def create_profile_on_user_creation(sender, instance, created, **kwargs) -> None:
    if created:
        TrackerProfile.objects.create(user=instance)


@receiver(post_save, sender="terminusgps_tracker.TrackerProfile")
def create_starter_objects_on_profile_creation(
    sender, instance, created, **kwargs
) -> None:
    if created:
        TrackerSubscription.objects.create(profile=instance, tier=None)
        TrackerShippingAddress.objects.create(profile=instance)
        TrackerTodoList.objects.create(profile=instance)


@receiver(post_save, sender="terminusgps_tracker.TrackerTodoList")
def create_starter_todos(sender, instance, created, **kwargs) -> None:
    if created:
        TodoItem.objects.create(
            label="Upload a payment method", view="payments", todo_list=instance
        )
        TodoItem.objects.create(
            label="Register your first asset", view="assets", todo_list=instance
        )
        TodoItem.objects.create(
            label="Upload your shipping address", view="shipping", todo_list=instance
        )
        TodoItem.objects.create(
            label="Select a subscription",
            view="tracker subscriptions",
            todo_list=instance,
        )
