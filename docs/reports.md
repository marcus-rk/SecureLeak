# Reports and Uploads (Phase 3–4)

A focused reference for the reports feature and the optional image upload added in Phase 4. Keep it simple, secure, and exam‑friendly.

## Data model

Table: `reports`

- `id` (pk)
- `owner_id` (fk → users.id)
- `title` (text, required)
- `description` (text, required)
- `severity` (text: `low|medium|high`)
- `status` (text: `public|private|closed`)
- `image_name` (text, nullable) — randomized stored filename for a single optional image
- `created_at` (timestamp)

Notes:
- `image_name` stores only the sanitized, randomized filename. The path is derived as `uploads/<report_id>/<image_name>`.

## Routes

- `GET /reports` — list
  - Requires login. Shows public reports + your own private reports (auth everywhere).

- `GET /reports/new` — form
  - Requires login. Includes CSRF token and supports file upload (multipart form).

- `POST /reports/new` — create
  - Requires login (CSRF‑protected). Validates title, description, severity, and status (`public|private`).
  - Optional `image` file input.
  - On success: 303→`/reports` (PRG).
  - On error: 400 with a friendly flash.

- `GET /reports/<id>` — detail
  - Requires login. Visible if report is public or you are the owner of a private report; otherwise 404.

- `GET /reports/file/<report_id>/<name>` — serve image
  - Requires login. Same visibility rule as detail.
  - Only serves when `name` equals the DB‑stored `image_name` for that report.
  - Inline display (`send_from_directory(..., as_attachment=False)`).

## Uploads: constraints (KISS)

- One optional image per report (stored as `image_name`).
- Validation:
  - Extension allowlist: `.png`, `.jpg`, `.jpeg`, `.gif` (lowercased)
  - MIME prefix: `image/`
  - Size cap: 2 MiB (checked via `request.content_length` when present)
- Storage:
  - Outside `/static`: `uploads/<report_id>/<randomname>.<ext>`
  - Filenames: `secrets.token_hex()` + `secure_filename`
- Visibility:
  - Public → any logged‑in user can fetch
  - Private → only the owner; unauthorized users get 404 (not 403)
- Fail‑safe:
  - If saving fails after creating the report, we show a warning and keep the report (no complex transactions).

## Templates

- `templates/report_new.html` — multipart form with `<input name="image" accept="image/*">`
- `templates/report_detail.html` — displays thumbnail when `image_name` is present via the secure file route

## Configuration

- Base uploads directory is configurable via app config (and `.env`):
  - `.env`: `UPLOADS_DIR=uploads` (or `instance/uploads` if preferred)
  - `security/uploads.py` reads `current_app.config["UPLOADS_DIR"]`
- Tests can override `app.config["UPLOADS_DIR"]` to a temporary folder per test run.

## Security notes (see also `docs/security_model.md`)

- CSRF: forms include `{{ csrf_token() }}`; POSTs are validated by Flask‑WTF.
- Authorization: a shared helper enforces visibility for detail and file routes.
- Path safety: only serve `image_name` stored in DB; never trust user paths.
- XSS: images are served as files and templates remain auto‑escaped (no `|safe`).

## Testing hints

- Use `https` base_url and `Referer` headers (as in the auth tests) to satisfy CSRF/Talisman.
- Override `UPLOADS_DIR` to a temp dir in tests for isolation.
- Minimal tests to keep:
  - Public image: owner and other can GET 200
  - Private image: non‑owner GET 404; owner GET 200
  - Disallowed extension: 400
