# Seed Pack (KISS)

This folder provides small, deterministic demo data for SecureLeak. It recreates a fresh database and inserts users, reports, comments, and a sprinkling of images.

All seeded user passwords are literally: `password`.

## Contents

- `users.csv` — base users (2 admins + 10–16 developers)
- `report_titles.txt` — ~30 report titles
- `report_snippets.txt` — ~30 short lines to assemble descriptions
- `comment_snippets.txt` — ~25 conversational comment lines
- `images/` — pre-committed PNGs used for attachments (add ~5–8 small demo images)
- `seed_runner.py` — CLI seeder (deterministic; RNG seed = 42)
 

## What it creates

- Users: 12–18 total (2 admins: admin1@admin.com, admin2@admin.com; everyone uses password `password`)
- Reports: 35–55 across all users
  - status distribution: ~55% public, ~35% private, ~10% closed
  - severity distribution: ~25% low, ~45% medium, ~30% high
  - images on ~30–40% of reports (one image/report)
- Comments: up to ~250 total; 0–8 per report (skewed to 0–3)

Visibility integrity:
- Private reports are owned by many different users (not just one)
- Closed reports may have comments added before closing (we do not restrict seed comments timing)

Determinism: RNG seed = 42 → same dataset each run.

## How to run

This will remove the current SQLite file and re-create everything.

```bash
# From the repo root, with your venv active
python -m seed.seed_runner
```

or

```bash
python3 seed/seed_runner.py
```

What it does:
1) Deletes the current SQLite file configured by the app (`app.config['DATABASE']`).
2) Applies `database/migrations/init.sql`.
3) Inserts users (hashing password via Argon2id), reports, comments, and optional images.
4) Prints summary counts.

Idempotency: The script always recreates the DB from scratch for a clean state.

If `seed/images` is empty, the seeder simply skips attaching images. To include images,
add a handful of tiny PNGs. Suggested naming: `bug_01.png`, `poc_auth_bypass.png`, `csrf_demo.png`.

## Notes

- The script avoids raw SQL for inserts/updates and uses repository functions where possible.
- Images are read from `seed/images`. If the folder is empty, no images are attached.
- Keep it small and fast so tests and demos run quickly.
