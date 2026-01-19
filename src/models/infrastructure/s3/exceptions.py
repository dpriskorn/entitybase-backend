class S3StorageError(Exception):
    """Base exception for S3 storage operations."""

    pass


class S3NotFoundError(S3StorageError):
    """Raised when S3 object is not found."""

    pass


class S3ConnectionError(S3StorageError):
    """Raised when S3 connection fails."""

    pass
