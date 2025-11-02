from typing import Callable, Mapping
from argon2 import PasswordHasher


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
