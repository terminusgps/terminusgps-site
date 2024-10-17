from typing import Any
from django.forms.widgets import MultiWidget


class TerminusAddressWidget(MultiWidget):
    def decompress(self, value: Any) -> Any | None:
        return [None]

    def compress(self, *args, **kwargs):
        return super().compress(*args, **kwargs)
