
# Seed Pack — Hacker‑Style (KISS)

Goal: compact, realistic seed data for a public‑facing security research site. Tone is informal, concise, and community‑oriented. Every seeded account uses the password: `password`.

## Folder layout

```
/seed/
  README.md
  users.csv
  report_titles.txt
  report_snippets.txt
  comment_snippets.txt
  images/                # 5–8 small PNGs you add + README.txt
```

## What’s included

- Users: playful, hacker‑y display names; 2–3 admins, rest users
- Reports: 35–55 with mixed severity and status
- Comments: short, helpful thread lines with a casual tone
- Images: optional; attached to ~35% of reports if present

## Users format (this repo)

CSV header expected by the seeder: `email,name,role`

- `email`: any fake address (we use `@mail.com`)
- `name`: display name; username is auto‑slugified from this
- `role`: `admin` or `user`
- Password for every account is literally `password` (hashed during seeding)

Note: older docs sometimes show `email,username,display_name,role`. In this project the seeder reads `email,name,role` and generates the username from `name`.

## Images

Put 5–8 small PNGs in `seed/images/` with descriptive names, e.g.

```
bug_01.png
poc_auth_bypass.png
sqli_console.png
csrf_flow.png
stacktrace_500.png
```

Tips:
- Keep each image small (<100 KB) so the repo stays light
- Avoid the prefix `placeholder_` — the seeder ignores files named `placeholder_*.png`
- PNG only; MIME is set to `image/png` by the seeder

If no images are present, seeding still works; reports are created without attachments.

## How to run

Run the seeder to reset the database and load demo content:

```
python seed/seed_runner.py
```

What it does:
1) Drops the existing SQLite DB and recreates schema
2) Wipes the uploads directory
3) Loads `users.csv`, `report_titles.txt`, `report_snippets.txt`, `comment_snippets.txt`
4) Creates 35–55 reports at random, adds comments, and (optionally) attaches images

That’s it — fast, deterministic, and ready to demo.
 

## What it creates

- Users: 12–18 total (2 admins: admin1@mail.com, admin2@mail.com; everyone uses password `password`)
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
