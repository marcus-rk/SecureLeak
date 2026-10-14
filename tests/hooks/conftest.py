import subprocess
from pathlib import Path

import pytest

SYSTEM_PYTHON = "/usr/bin/python3"


@pytest.fixture
def legacy_python() -> str:
    """Path of /usr/bin/python3 when it is older than 3.10, else skip (the hooks must run there)."""
    if not Path(SYSTEM_PYTHON).is_file():
        pytest.skip(f"{SYSTEM_PYTHON} not found")
    code = "import sys; print(sys.version_info >= (3, 10))"
    result = subprocess.run([SYSTEM_PYTHON, "-c", code], capture_output=True, text=True, timeout=30)
    if result.stdout.strip() != "False":
        pytest.skip(f"{SYSTEM_PYTHON} is 3.10 or newer")
    return SYSTEM_PYTHON
