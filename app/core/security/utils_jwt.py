import jwt

from app.core.settings.jwt import auth_jwt


def encode_jwt(payload: dict, private_key: str = auth_jwt.private_key_path.read_text(), algorithm: str = auth_jwt.algorithm):
    return jwt.encode(
        payload=payload,
        key=private_key,
        algorithm=algorithm,
    )


def decode_jwt(token: str | bytes, public_key: str = auth_jwt.public_key_path.read_text(), algorithm: str = auth_jwt.algorithm):
    return jwt.decode(
        jwt=token,
        key=public_key,
        algorithms=[algorithm],
    )
