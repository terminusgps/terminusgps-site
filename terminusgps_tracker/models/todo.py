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

    class Meta:
        verbose_name = "to-do item"
        verbose_name_plural = "to-do items"

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

    class Meta:
        verbose_name = "to-do list"
        verbose_name_plural = "to-do lists"

    def __str__(self) -> str:
        return f"{self.profile.user.first_name}'s To-Do List"
