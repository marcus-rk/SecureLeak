# Image Sanitization (Privacy & Safety)

This document details the image processing strategy used to protect user privacy and server integrity.

## The Problem

Allowing users to upload raw images presents three major risks:
1.  **Privacy Leakage (EXIF Data)**: Photos often contain metadata like GPS coordinates, camera serial numbers, and timestamps. Publishing this can "dox" a whistleblower.
2.  **Malicious Payloads**: An attacker might embed malicious code (polyglot files) within an image file that executes when processed by a vulnerable library.
3.  **Decompression Bombs (Pixel Floods)**: An attacker might upload a small file (e.g., 100KB) that decompresses into a massive image (e.g., 20,000x20,000 pixels), exhausting server RAM and causing a crash.

## The Solution: Sanitization via Re-encoding

We use the **Pillow (PIL)** library to sanitize every uploaded image in `security/uploads.py`.

### Mechanism
Instead of just validating the file extension, we perform a "transcoding" step:
1.  **Open**: The file is opened and parsed by Pillow (verifying it is a valid image).
2.  **Dimension Check**: We verify that the image width and height do not exceed `MAX_IMAGE_DIMENSION` (2048px).
3.  **Strip**: We create a new, blank image canvas.
4.  **Copy**: We copy *only* the pixel data from the source to the new canvas.
5.  **Save**: We save this new image to disk.

### Code Snippet
```python
# security/uploads.py
    # Sanitize image: Open with Pillow, strip metadata, and save fresh
    # This removes EXIF data (GPS, camera info) and re-encodes the pixels
    with Image.open(file) as img:
        if img.width > MAX_IMAGE_DIMENSION or img.height > MAX_IMAGE_DIMENSION:
            raise ValueError(f"Image dimensions too large. Max {MAX_IMAGE_DIMENSION}x{MAX_IMAGE_DIMENSION} pixels.")

        # Convert to RGB to handle PNGs with transparency if saving as JPEG,
        # but here we keep original format. Pillow saves without metadata by default.
        # We create a new image to ensure no hidden data is copied over.
        data = list(img.getdata())
        clean_img = Image.new(img.mode, img.size)
        clean_img.putdata(data)
        clean_img.save(str(dest_path))
```

## Benefits

*   **Metadata Removal**: EXIF tags are not copied to the new image, effectively stripping GPS and other sensitive data.
*   **Payload Neutralization**: Any non-pixel data (like hidden scripts or appended binaries) is discarded.

## Reflections

*   **Performance**: Re-encoding is CPU-intensive. For a high-traffic site, this should be offloaded to a background worker (e.g., Celery) to avoid blocking the web request.
*   **Lossiness**: Re-saving JPEGs introduces generation loss. For a whistleblowing site, this trade-off (security > perfect quality) is acceptable.
