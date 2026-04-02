from argon2 import PasswordHasher
from argon2.exceptions import VerificationError

ph = PasswordHasher()


def hash_password(senha: str) -> str:
    return ph.hash(senha)


def verify_password(password: str, db_password: str) -> bool:
    try:
        ph.verify(hash=db_password, password=password)
        return True

    except VerificationError:
        return False
