import json
from wialon.api import WialonError

from terminusgps_tracker.wialonapi.items.base import WialonBase
from terminusgps_tracker.wialonapi.items.user import WialonUser
from terminusgps_tracker.wialonapi.items.unit import WialonUnit

class WialonNotificationAction:
    @staticmethod
    def create_email(to_addr: str, subject: str, html: bool = False, img_attach: bool = False) -> dict[str, str | dict[str, str]]:
        return {
            "t": "email",
            "p": {
                "email_to": to_addr,
                "html": str(int(html)),
                "img_attach": str(int(img_attach)),
                "subj": subject,
            }
        }

    @staticmethod
    def create_sms(to_numbers: str) -> dict[str, str | dict[str, str]]:
        return {
            "t": "sms",
            "p": {
                "phones": ";".join(to_numbers.split(","))
            }
        }

    @staticmethod
    def create_mobile_notification(app_name: str, user: WialonUser) -> dict[str, str | dict[str, str]]:
        return {
            "t": "mobile_apps",
            "p": {
                "apps": json.dumps({
                    app_name: [user.id]
                })
            }
        }

    @staticmethod
    def create_telegram_notification(channel_id: str, telegram_token: str) -> dict[str, str | dict[str, str]]:
        return {
            "t": "messenger_messages",
            "p": {
                "chat_id": channel_id,
                "token": telegram_token,
            }
        }
 
    @staticmethod
    def create_register_event_for_unit(is_violation: bool = False) -> dict[str, str | dict[str, str]]:
        return {
            "t": "event",
            "p": {"flags": str(1) if is_violation else str(0)},
        }

    @staticmethod
    def create_command_execution(command_type: str, link_type: str, command_name: str, parameters: str) -> dict[str, str | dict[str, str]]:
        return {
            "t": "exec_cmd",
            "p": {
                "cmd_type": command_type,
                "link": link_type,
                "name": command_name,
                "param": parameters,
            }
        }

    @staticmethod
    def create_video_upload(url: str, video_duration: int = 60, channel_mask: str = "") -> dict[str, str | dict[str, str]]:
        return {
            "t": "video_service",
            "p": {
                "channel_mask": channel_mask,
                "duration": str(video_duration),
                "base_url": url,
            }
        }

    @staticmethod
    def create_access_change(units: list[WialonUnit], users: list[WialonUser], acl_bits: int, acl_mask: int) -> dict[str, str | dict[str, str]]:
        if not units or users:
            raise ValueError
        else:
            return {
                "t": "user_access",
                "p": {
                    "acl_bits": str(acl_bits),
                    "acl_mask": str(acl_mask),
                    "units": ",".join([str(unit.id) for unit in units]),
                    "users": ",".join([str(user.id) for user in users]),
                }
            }

    @staticmethod
    def create_send_request(url: str, is_get_request: bool = False) -> dict[str, str | dict[str, str]]:
        return {
            "t": "push_messages",
            "p": {
                "url": url,
                "get": str(int(is_get_request)),
            }
        }

class WialonNotification(WialonBase):
    def create(self, **kwargs) -> None:
        if kwargs.get("resource", None) is None:
            raise ValueError("Tried to create a notification but resource was none.")
        if kwargs.get("name", None) is None:
            raise ValueError("Tried to create a notification but name was none.")
        if kwargs.get("units", None) is None:
            raise ValueError("Tried to create a notification but units were none.")
        if kwargs.get("action_type", None) is None:
            raise ValueError("Tried to create a notification but action_type was none.")

        try:
            ...
        except WialonError as e:
            raise e
