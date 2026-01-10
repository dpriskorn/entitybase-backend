import os

from typing import NoReturn, Optional


def raise_validation_error(
    message: str,
    status_code: int = 400,
    exception_class: Optional[type[Exception]] = None,
) -> NoReturn:
    """Raise exception based on ENVIRONMENT and optional exception_class.

    HTTPException is only raised in production when explicitly requested.
    In development, HTTPException requests fall back to ValueError.
    """
    from fastapi import HTTPException

    is_prod = os.getenv("ENVIRONMENT", "dev").lower() == "prod"

    if exception_class is not None:
        if exception_class == HTTPException and is_prod:
            raise HTTPException(status_code=status_code, detail=message)
        else:
            # In dev, or if not HTTPException, raise the specified exception
            raise exception_class(message)
    else:
        if is_prod:
            raise HTTPException(status_code=status_code, detail=message)
        else:
            raise ValueError(message)
