from dataclasses import dataclass


@dataclass
class QuickbooksAuthorizationResponse:
    auth_code: str
    realm_id: str
    state: str


@dataclass
class QuickbooksAuthorizationResponseError:
    error: str
    error_description: str
    state: str
