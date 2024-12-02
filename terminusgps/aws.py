import json

from boto3.session import Session


def get_secret(
    secret_name: str, profile: str | None = None, region_name: str = "us-east-1"
) -> dict[str, str]:
    profile_name = profile if profile is not None else "Blake Nall"
    client = Session(profile_name=profile_name).client(
        service_name="secretsmanager", region_name=region_name
    )
    secret = client.get_secret_value(SecretId=secret_name)["SecretString"]
    return json.loads(secret)
