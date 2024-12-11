from typing import Any
import datetime
import boto3
import json
import jwt


def get_secret(name: str, region: str = "us-east-1") -> dict[str, str]:
    client = boto3.Session().client(service_name="secretsmanager", region_name=region)
    secret = client.get_secret_value(SecretId=name)["SecretString"]
    return json.loads(secret)


def generate_support_jwt(
    widget_id: int, connect_secret: str, expires_in: int = 500
) -> str:
    headers: dict[str, str] = {"typ": "JWT", "alg": "HS256"}
    payload: dict[str, Any] = {
        "sub": widget_id,
        "iat": datetime.datetime.now(),
        "exp": datetime.datetime.now() + datetime.timedelta(seconds=expires_in),
        "segmentAttributes": {"connect:Subtype": {"ValueString": "connect:Guide"}},
        "attributes": {"name": "terminusgps-site", "email": "support@terminusgps.com"},
    }
    encoded_token = jwt.encode(
        payload, connect_secret, algorithm="HS256", headers=headers
    )
    return encoded_token
