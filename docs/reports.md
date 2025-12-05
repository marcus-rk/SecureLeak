# Reports and Uploads

This document details the implementation of the core reporting feature and the secure file upload system.

---

## 📊 Data Model

**Table**: `reports`

| Column | Type | Description |
|:---|:---|:---|
| `id` | Integer (PK) | Unique identifier |
| `owner_id` | Integer (FK) | Link to `users.id` |
| `title` | Text | Required |
| `description` | Text | Required |
| `severity` | Text | `low`, `medium`, `high` |
| `status` | Text | `public`, `private`, `closed` |
| `image_name` | Text | Randomized filename (nullable) |
| `created_at` | Timestamp | Auto-generated |

---

## 🛡️ Secure Database Access

All database interactions go through the `repository` layer, which strictly uses **parameterized queries** to prevent SQL Injection.

```python
# repository/reports_repo.py
def create_report(owner_id: int, title: str, description: str, severity: str, status: str) -> int:
    db = get_db()
    cur = db.execute(
        "INSERT INTO reports (owner_id, title, description, severity, status) VALUES (?, ?, ?, ?, ?)",
        (owner_id, title, description, severity, status),
    )
    db.commit()
    return cur.lastrowid
```

---

## 📂 Secure File Uploads

We implement a strict "Defense-in-Depth" strategy for file uploads to prevent malicious files from compromising the server.

### 1. Validation & Sanitization
We don't just check the extension; we re-process the image.

```python
```python
# security/uploads.py
def store_report_image(file: FileStorage, report_id: int, base_dir: Optional[str] = None) -> str:
    # ...
    ext = get_ext(file.filename or "")
    rnd = secrets.token_hex(16) + ext
    dest_name = secure_filename(rnd)
    
    # ...
    
    # Sanitize image: Open with Pillow, strip metadata, and save fresh
    with Image.open(file) as img:
        # Convert to RGB to handle PNGs with transparency if saving as JPEG,
        # but here we keep original format. Pillow saves without metadata by default.
        # We create a new image to ensure no hidden data is copied over.
        data = list(img.getdata())
        clean_img = Image.new(img.mode, img.size)
        clean_img.putdata(data)
        clean_img.save(str(dest_path))

    return dest_name
```
### 2. Storage Isolation
*   **Location**: Uploads are stored **outside** the `static/` folder (`uploads/`).
*   **Serving**: Files are served via a controlled route that checks permissions, not directly by the web server.

### 3. Access Control
*   **Public Reports**: Images are accessible to all logged-in users.
*   **Private Reports**: Images are only accessible to the owner. Unauthorized access returns `404 Not Found` to avoid leaking existence.

---

## 🚦 Routes & Logic

| Method | Route | Description | Security Checks |
|:---|:---|:---|:---|
| `GET` | `/reports` | List reports | Shows public + own private reports. |
| `POST` | `/reports/new` | Create report | CSRF check, Input Validation, Rate Limit. |
| `GET` | `/reports/<id>` | View report | Checks `is_report_viewable(user, report)`. |
| `GET` | `/reports/<id>/image/<name>` | Serve image | Checks ownership/visibility before serving. |

---

## 🧪 Testing Strategy

*   **CSRF**: Tests must use `client.post(..., follow_redirects=True)` and handle CSRF tokens.
*   **Isolation**: Tests override `UPLOADS_DIR` to a temporary directory to avoid cluttering the dev environment.
*   **Permissions**: We explicitly test that User A cannot view User B's private report.
