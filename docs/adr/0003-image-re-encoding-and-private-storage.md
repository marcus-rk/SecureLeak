# 0003. Images are re-encoded and stored outside static

Status: accepted
Recorded: 2026-10. Decided: 2025-11-03 (66b3e03) for random names and private storage, 2025-12-04 (9301c6f) for re-encoding

An image gets a random name (`security/uploads.py:47`) and is stored per report under `uploads/<report_id>/`, outside `static/` (`security/uploads.py:50-52`, `docs/reports.md:76`). It is served only through the image route, which applies the visibility policy (`routes/reports.py:135-153`). The re-encode by Pillow (`security/uploads.py:56-67`) came in 9301c6f (2025-12-04) and the 2048px dimension cap (`security/uploads.py:14`) in 4dd3214 (2025-12-10).

## Why

- Guards against the three threats named in [image_sanitization.md](../image_sanitization.md): the re-encode drops EXIF metadata that leaks privacy and payloads hidden in polyglot files; the dimension cap (`security/uploads.py:58-59`) stops decompression bombs.
- Random names and storage outside `static/` served through that route prevent path traversal, prevent filename collisions, and make private images obey the visibility policy.

## Considered options

- Extension and MIME checks only, with no re-encode: "considered, but not for PoC" (maintainer's words).
- An external store such as S3 or a CDN: "considered, but not for PoC" (maintainer's words).
- Antivirus or content sniffing (python-magic): "considered, but not for PoC" (maintainer's words).
- Storing images as database blobs: "considered, but not for PoC" (maintainer's words).

## Consequences

- `tests/reports/test_uploads.py::test_upload_disallowed_extension_returns_400` rejects a `.txt` file sent as `text/plain`, so it passes on either the extension or the MIME check; the extension allowlist alone is not enforced by a test.
- The visibility policy on the image route is partly enforced by `tests/reports/test_uploads.py::test_upload_public_and_private_access` (public and private reports only; closed reports and admins are not enforced by a test).
- The re-encode, the dimension cap and the random name are not enforced by a test.

If reversed: serving from `static/` bypasses the visibility policy ([ADR 0002](./0002-single-visibility-policy.md)) for private reports; keeping client-supplied filenames reopens traversal and collisions; dropping the re-encode keeps EXIF and payloads. Do not "optimise" by skipping the re-encode or moving images under `static/`.
