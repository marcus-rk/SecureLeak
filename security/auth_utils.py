from typing import Callable, Mapping, Optional
from argon2 import PasswordHasher
from email_validator import EmailNotValidError, validate_email


def build_hasher() -> PasswordHasher:
    """Create a PasswordHasher with explicit Argon2id parameters."""
    return PasswordHasher(
        time_cost=3,
        memory_cost=65536,  # 64 MiB
        parallelism=2,
        hash_len=32,
        salt_len=16,
    )

def normalize_email(s: str) -> str:
    return (s or "").strip().lower()


def normalize_and_validate_email(s: str) -> Optional[str]:
    """Validate and normalize an email address.

    - Returns a canonical, normalized address (IDNA domain, case-folded) on success.
    - Returns None if invalid. Deliverability checks are disabled for speed/offline tests.
    """
    try:
        result = validate_email((s or "").strip(), check_deliverability=False)
        # email-validator already normalizes; ensure lower for DB uniqueness invariants
        return result.normalized.lower()
    except EmailNotValidError:
        return None


def verify_password(hasher: PasswordHasher, stored_hash: str, candidate: str) -> bool:
    """Return True when candidate matches stored_hash."""
    try:
        return bool(hasher.verify(stored_hash, candidate))
    except Exception:
        return False


def maybe_upgrade_hash(
    hasher: PasswordHasher,
    user_row: Mapping[str, object],
    password: str,
    update_fn: Callable[..., None],
) -> None:
    """If the stored hash is outdated, rehash and persist via update_fn."""
    try:
        stored = user_row.get("password_hash")  # type: ignore[assignment]
        if stored and hasher.check_needs_rehash(stored):
            new_hash = hasher.hash(password)
            update_fn(user_row["id"], password_hash=new_hash)  # type: ignore[arg-type]
    except Exception:
        return


def validate_password(password: str, min_len: int = 10) -> bool:
    """Return True if password meets minimal rules; False otherwise."""
    if not isinstance(password, str):
        return False
    if len(password) < min_len:
        return False
    return True
