from django.db import models
from django.urls import reverse


class TodoItem(models.Model):
    todo_list = models.ForeignKey(
        "terminusgps_tracker.TrackerTodoList",
        on_delete=models.CASCADE,
        related_name="todo_items",
    )
    label = models.CharField(max_length=64)
    view = models.CharField(max_length=512)
    is_complete = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.label

    def get_absolute_url(self) -> str:
        return reverse(self.view)


class TrackerTodoList(models.Model):
    profile = models.OneToOneField(
        "terminusgps_tracker.TrackerProfile",
        on_delete=models.CASCADE,
        related_name="todo_list",
    )

    def __str__(self) -> str:
        return f"{self.profile.user.first_name}'s To-Do List"
