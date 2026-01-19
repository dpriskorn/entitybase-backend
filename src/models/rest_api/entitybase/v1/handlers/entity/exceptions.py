"""Entity processing errors."""


class EntityProcessingError(Exception):
    """Custom exception for entity processing errors."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)