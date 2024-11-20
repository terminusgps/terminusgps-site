from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from terminusgps_tracker.models import TrackerProfile
from terminusgps_tracker.models.todo import TodoItem


@receiver(post_save, sender=get_user_model())
def create_tracker_profile(sender, instance, created, **kwargs) -> None:
    if created:
        TrackerProfile.objects.create(user=instance)


@receiver(post_save, sender="terminusgps_tracker.TrackerTodoList")
def create_starter_todos(sender, instance, created, **kwargs) -> None:
    if created:
        TodoItem.objects.create(
            label="Register your first asset",
            view="profile create asset",
            todo_list=instance,
        )
        TodoItem.objects.create(
            label="Upload a payment method",
            view="profile create payment",
            todo_list=instance,
        )
        TodoItem.objects.create(
            label="Select a subscription",
            view="tracker subscriptions",
            todo_list=instance,
        )
