from typing import Any
from django.template import Library

from terminusgps.wialon.session import WialonSession
from terminusgps_tracker.models import TrackerAsset

register = Library()


@register.inclusion_tag("terminusgps_tracker/assets/image.html")
def get_asset_icon(asset: TrackerAsset, css_class: str | None = None) -> dict[str, Any]:
    base_url = "http://hst-api.wialon.com/avl_item_image/%(asset_id)s/%(max_size)s/%(filename)s.png?b=%(border_size)s&v=%(as_png)s&sid=%(sid)s"
    with WialonSession() as session:
        target_url = base_url % {
            "asset_id": asset.wialon_id,
            "max_size": 32,
            "filename": "icon",
            "border_size": 2,
            "as_png": "true",
            "sid": session.id,
        }
    return {"url": target_url, "class": str(css_class)}
