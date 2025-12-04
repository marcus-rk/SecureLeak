from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize Limiter with default key (IP address)
# We use in-memory storage for simplicity
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)
