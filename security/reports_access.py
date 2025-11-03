from __future__ import annotations

from typing import Optional


def is_report_viewable(report: dict, user_id: Optional[int]) -> bool:
    """Return True if the report is viewable by the given user.

    Policy: public → any authenticated user; private → only the owner.
    """
    if not report:
        return False
    status = report.get("status")
    if status == "public":
        return True
    if status == "private":
        return user_id is not None and user_id == report.get("owner_id")
    # Unknown status: default deny
    return False
