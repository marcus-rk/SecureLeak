# Security.txt (Vulnerability Disclosure)

This document explains the implementation of the `security.txt` standard in SecureLeak.

## What is security.txt?

`security.txt` (RFC 9116) is a standardized file that tells security researchers how to responsibly report vulnerabilities to an organization. It is the "robots.txt" for security.

## Implementation

We serve this file at the standard location: `/.well-known/security.txt`.

### Content
The file (`security/security.txt`) contains:
*   **Contact**: The contact for reporting bugs (see the `Contact` field in `security/security.txt`).
*   **Expires**: A date after which the information is considered stale (forcing regular review).
*   **Preferred-Languages**: Helping researchers know which language to write in.
*   **Policy**: A link to the project's vulnerability reporting policy.

### Technical Setup
A dedicated route in `app.py` reads the static file and serves it with the correct `Content-Type: text/plain` header.

## Why this matters

*   **Professionalism**: It signals that we take security seriously and welcome feedback.
*   **Safe Harbor**: It implicitly (or explicitly via the `Policy` link) offers legal protection to researchers who follow the rules, encouraging them to report bugs rather than exploit them.

## Reflections

*   **Maintenance**: The `Expires` field is critical. If we forget to update it, researchers might assume the program is dead. This update should be part of the CI/CD pipeline or a calendar reminder.
*   **Verification**: In a real deployment, we would digitally sign this file (creating `security.txt.sig`) to prove it wasn't planted by an attacker who compromised the web server.
