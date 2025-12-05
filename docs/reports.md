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
def create_report(owner_id, title, description, severity, status):
    db = get_db()
    # ? placeholders prevent SQL Injection
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
# security/uploads.py
def store_report_image(file_storage, report_id, base_dir):
    # 1. Generate secure random filename
    ext = get_ext(file_storage.filename)
    random_name = f"{secrets.token_hex(16)}{ext}"
    
    # 2. Sanitize content with Pillow (strips EXIF/metadata)
    img = Image.open(file_storage)
    img.verify()  # Check if it's really an image
    
    # Re-open and save to new buffer to strip metadata
    file_storage.seek(0)
    img = Image.open(file_storage)
    img.save(destination_path)
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
