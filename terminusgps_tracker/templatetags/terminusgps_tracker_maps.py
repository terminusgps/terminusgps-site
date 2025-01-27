from django.template import Library

from terminusgps.wialon.session import WialonSession
from wialon.api import WialonError
from terminusgps_tracker.models import TrackerAsset

register = Library()


@register.inclusion_tag("terminusgps_tracker/assets/map.html")
def asset_map(
    asset: TrackerAsset, zoom: int = 10, css_class: str | None = None
) -> dict[str, str]:
    try:
        with WialonSession() as session:
            session.wialon_api.events_update_units(
                **{
                    "mode": "add",
                    "units": [{"id": asset.wialon_id, "detect": {"*": 0}}],
                }
            )
            return {
                "map_url": f"http://hst-api.wialon.com/avl_render/2_2_{zoom}/{session.id}.png",
                "class": str(css_class),
            }
    except (WialonError, ValueError) as e:
        print(e)
        raise
