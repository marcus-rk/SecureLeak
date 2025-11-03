from __future__ import annotations

import os
import secrets
from pathlib import Path
from typing import Optional, Tuple

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

ALLOWED_EXTS = {".png", ".jpg", ".jpeg", ".gif"}
MAX_UPLOAD_BYTES = 2 * 1024 * 1024  # 2 MiB


def uploads_base_dir() -> str:
    """Base directory for uploads; configurable for tests."""
    return current_app.config.get("UPLOADS_DIR", "uploads")


def get_ext(filename: str) -> str:
    return Path(filename).suffix.lower()


def is_allowed_ext(ext: str) -> bool:
    return ext in ALLOWED_EXTS


def is_allowed_mimetype(mimetype: Optional[str]) -> bool:
    return bool(mimetype) and mimetype.startswith("image/")


def max_upload_bytes() -> int:
    return MAX_UPLOAD_BYTES


def store_report_image(file: FileStorage, report_id: int, base_dir: Optional[str] = None) -> str:
    """Save an uploaded image under uploads/<report_id>/ and return the stored filename.

    Assumes validation (ext/mimetype/size) has been performed by the caller.
    """
    if base_dir is None:
        base_dir = uploads_base_dir()

    ext = get_ext(file.filename or "")
    rnd = secrets.token_hex(16) + ext
    dest_name = secure_filename(rnd)

    report_dir = Path(base_dir) / str(report_id)
    report_dir.mkdir(parents=True, exist_ok=True)
    dest_path = report_dir / dest_name
    file.save(str(dest_path))
    return dest_name
