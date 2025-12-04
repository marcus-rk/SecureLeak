import csv
import os
import random
from datetime import datetime
from pathlib import Path
from typing import List
import sys

# Allow running this file directly (python seed/seed_runner.py)
# by adding the project root to sys.path before importing app.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app  # noqa: E402
from database.connection import close_db  # noqa: E402
from database.initialize import apply as init_db  # noqa: E402
from repository import users_repo, reports_repo, comments_repo  # noqa: E402
from security.auth_utils import build_hasher  # noqa: E402
from security.uploads import store_report_image, uploads_base_dir  # noqa: E402


# Deterministic RNG
RNG_SEED = 42
random.seed(RNG_SEED)


def slugify_username(name: str, taken: set[str]) -> str:
    base = "".join(ch.lower() for ch in name if ch.isalnum() or ch in {"_", "."}).replace(" ", "")
    base = base or "user"
    candidate = base
    i = 2
    while candidate in taken:
        candidate = f"{base}{i}"
        i += 1
    taken.add(candidate)
    return candidate


def load_seed_images(seed_dir: Path) -> List[Path]:
    """Load pre-committed PNGs from /seed/images.

    If none are present, return an empty list. The seeder will continue and simply
    skip attaching images. To use richer demo images, add ~5–8 small PNGs with
    meaningful names (e.g., bug_01.png, poc_auth_bypass.png) into seed/images.
    """
    images_dir = seed_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    all_pngs = sorted(images_dir.glob("*.png"))
    # Prefer real demo images; ignore legacy placeholder_* files if present
    filtered = [p for p in all_pngs if not p.name.startswith("placeholder_")]
    return filtered or all_pngs


def main() -> None:
    app = create_app()
    with app.app_context():
        db_path = Path(app.config["DATABASE"]).resolve()
        # 1) Delete existing DB
        if db_path.exists():
            db_path.unlink()
        # Also clear uploads dir
        uploads_dir = Path(uploads_base_dir())
        if uploads_dir.exists():
            for child in uploads_dir.glob("**/*"):
                try:
                    if child.is_file():
                        child.unlink()
                except Exception:
                    pass
        # 2) Recreate schema
        init_db()

        # 3) Load seed data files
        seed_dir = Path(__file__).parent
        users_csv = seed_dir / "users.csv"
        titles_txt = seed_dir / "report_titles.txt"
        rep_snippets_txt = seed_dir / "report_snippets.txt"
        com_snippets_txt = seed_dir / "comment_snippets.txt"

        titles = [
            line.strip()
            for line in titles_txt.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        rep_snippets = [
            line.rstrip()
            for line in rep_snippets_txt.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        com_snippets = [
            line.strip()
            for line in com_snippets_txt.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        placeholder_images = load_seed_images(seed_dir)

        # 4) Insert users
        hasher = build_hasher()
        taken_usernames: set[str] = set()
        user_ids: List[int] = []
        with users_csv.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = (row["email"] or "").strip().lower()
                name = (row["name"] or "user").strip()
                role = (row["role"] or "user").strip().lower()
                username = slugify_username(name, taken_usernames)
                pwd_hash = hasher.hash("password123")
                uid = users_repo.create_user(email=email, password_hash=pwd_hash, username=username, role=role)
                user_ids.append(uid)

        # 5) Insert reports
        n_reports = random.randint(35, 55)
        severity_choices = ["low", "medium", "high"]
        severity_weights = [0.25, 0.45, 0.30]
        status_choices = ["public", "private", "closed"]
        status_weights = [0.55, 0.35, 0.10]

        report_ids: List[int] = []
        for _ in range(n_reports):
            owner_id = random.choice(user_ids)
            title = random.choice(titles)
            # Build a short description from snippets (3-6 lines)
            lines = random.sample(rep_snippets, k=random.randint(3, 6))
            description = "\n".join(lines)
            severity = random.choices(severity_choices, weights=severity_weights, k=1)[0]
            status = random.choices(status_choices, weights=status_weights, k=1)[0]
            rid = reports_repo.create_report(owner_id, title, description, severity, status)
            report_ids.append(rid)

            # Attach image to ~35% of reports (only if pre-committed images exist)
            if random.random() < 0.35 and placeholder_images:
                try:
                    # Pick a random seed image
                    src = random.choice(placeholder_images)
                    with src.open("rb") as f:
                        # store_report_image expects a FileStorage-like; emulate minimal API via a shim
                        class _FS:
                            def __init__(self, filename: str, data: bytes):
                                self.filename = filename
                                self.mimetype = "image/png"
                                self._data = data

                            def save(self, dst: str) -> None:
                                Path(dst).write_bytes(self._data)

                        fs = _FS(src.name, f.read())
                        dest_name = store_report_image(fs, rid, uploads_base_dir())
                        reports_repo.update_report(rid, {"image_name": dest_name})
                except Exception:
                    pass

        # 6) Insert comments (0–8 per report, skew toward 0–3)
        max_total_comments = 250
        total_comments = 0
        for rid in report_ids:
            if total_comments >= max_total_comments:
                break
            report = reports_repo.get_report_by_id(rid)
            if not report:
                continue
            # Skewed distribution: more zeros
            options = [0, 1, 2, 3, 4, 5, 6, 7, 8]
            weights = [0.25, 0.20, 0.18, 0.14, 0.08, 0.06, 0.04, 0.03, 0.02]
            n = random.choices(options, weights=weights, k=1)[0]
            for _ in range(n):
                if total_comments >= max_total_comments:
                    break
                if report["status"] == "private":
                    # Only owner comments on private reports (visibility integrity)
                    author_id = report["owner_id"]
                else:
                    author_id = random.choice(user_ids)
                body = random.choice(com_snippets)
                comments_repo.create_comment(rid, author_id, body)
                total_comments += 1

        # 7) Summary
        print("Seed complete:")
        print(f"  Users:   {len(user_ids)}")
        print(f"  Reports: {len(report_ids)}")
        print(f"  Comments:{total_comments}")

        # Ensure DB connection closes cleanly (must be inside app context)
        close_db()


if __name__ == "__main__":
    main()
