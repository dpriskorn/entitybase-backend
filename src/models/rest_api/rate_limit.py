"""Rate limiting utilities."""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

DEFAULT_RATE_LIMIT = "120/minute"
WRITE_RATE_LIMIT = "30/minute"
USER_RATE_LIMIT = "60/minute"
BATCH_RATE_LIMIT = "10/minute"
