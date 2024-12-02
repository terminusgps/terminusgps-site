from boto3.session import Session


def get_secret(secret_name: str, region_name: str = "us-east-1") -> str:
    client = Session(profile_name="Blake Nall").client(
        service_name="secretsmanager", region_name=region_name
    )
    secret = client.get_secret_value(SecretId=secret_name)["SecretString"]
    return secret


def get_secret_key(
    secret_name: str, secret_key: str, region_name: str = "us-east-1"
) -> str:
    client = Session(profile_name="Blake Nall").client(
        service_name="secretsmanager", region_name=region_name
    )
    secret = client.get_secret_value(SecretId=secret_name)["SecretString"]
    return secret.get(secret_key, "")
