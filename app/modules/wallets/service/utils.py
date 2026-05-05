import bcrypt


def hash_pin(pin: str) -> str:
    salt = bcrypt.gensalt()
    pin_hash = bcrypt.hashpw(pin.encode(), salt)
    return pin_hash.decode()


def verify_pin(pin: str, pin_hash: str) -> bool:
    try:
        return bcrypt.checkpw(pin.encode(), pin_hash.encode())
    except Exception:
        return False