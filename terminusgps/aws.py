from boto3.session import Session


def get_secret(secret_name: str, region_name: str = "us-east-1") -> str | None:
    client = Session(profile_name="Blake Nall").client(
        service_name="secretsmanager", region_name=region_name
    )
    secret: dict[str, str] | str = client.get_secret_value(SecretId=secret_name).get(
        "SecretString", ""
    )
    if isinstance(secret, str):
        return secret


def get_secret_key(
    secret_name: str, secret_key: str, region_name: str = "us-east-1"
) -> str | None:
    client = Session(profile_name="Blake Nall").client(
        service_name="secretsmanager", region_name=region_name
    )
    secret: dict[str, str] | str = client.get_secret_value(SecretId=secret_name).get(
        "SecretString", ""
    )
    if isinstance(secret, dict):
        return secret.get(secret_key, "")
