import json

from boto3.session import Session


def get_secret(name: str, profile: str, region: str = "us-east-1") -> dict[str, str]:
    client = Session(profile_name=profile).client(
        service_name="secretsmanager", region_name=region
    )
    secret = client.get_secret_value(SecretId=name)["SecretString"]
    return json.loads(secret)
