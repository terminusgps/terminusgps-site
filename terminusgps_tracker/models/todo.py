from django.db import models
from django.urls import reverse


class TodoItem(models.Model):
    label = models.CharField(max_length=64)
    view = models.CharField(max_length=512)
    is_complete = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.label

    @property
    def url(self) -> str:
        return reverse(self.view)


class TrackerTodoList(models.Model):
    items = models.ManyToManyField(TodoItem)
    profile = models.OneToOneField(
        "terminusgps_tracker.TrackerProfile", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.profile.user.username}'s To-do List"
