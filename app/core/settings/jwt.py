from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parents[2]


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = 'RS256'


auth_jwt = AuthJWT()