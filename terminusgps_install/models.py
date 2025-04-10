from django.db import models


class WialonAccount(models.Model):
    name = models.CharField(max_length=128)
    wialon_id = models.IntegerField()

    def __str__(self) -> str:
        return self.name


class WialonAsset(models.Model):
    name = models.CharField(max_length=128)
    wialon_id = models.IntegerField()
    account = models.ForeignKey(
        "terminusgps_install.WialonAccount",
        on_delete=models.CASCADE,
        related_name="assets",
    )

    def __str__(self) -> str:
        return self.name
