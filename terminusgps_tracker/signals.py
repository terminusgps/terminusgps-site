from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from terminusgps_tracker.integrations.wialon.items import WialonUnitGroup
from terminusgps_tracker.integrations.wialon.session import WialonSession
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
            label="Enter your shipping address", view="shipping", todo_list=instance
        )
        TodoItem.objects.create(
            label="Upload a payment method", view="payments", todo_list=instance
        )
        TodoItem.objects.create(
            label="Register your first asset", view="assets", todo_list=instance
        )
        TodoItem.objects.create(
            label="Select your subscription",
            view="tracker subscriptions",
            todo_list=instance,
        )


@receiver(post_save, sender="terminusgps_tracker.TrackerProfile")
def complete_todos(sender, instance, created, **kwargs) -> None:
    if instance.address.authorizenet_id:
        todo_item = instance.todo_list.todo_items.get(view="shipping")
        todo_item.is_complete = True
        todo_item.save()

    if instance.payments.filter().exists():
        todo_item = instance.todo_list.todo_items.get(view="payments")
        todo_item.is_complete = True
        todo_item.save()

    if instance.subscription.curr_tier:
        todo_item = instance.todo_list.todo_items.get(view="tracker subscriptions")
        todo_item.is_complete = True
        todo_item.save()

    with WialonSession() as session:
        unit_group = WialonUnitGroup(id=str(instance.wialon_group_id), session=session)
        if unit_group.items:
            todo_item = instance.todo_list.todo_items.get(view="assets")
            todo_item.is_complete = True
            todo_item.save()
