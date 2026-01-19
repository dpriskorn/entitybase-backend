from pydantic import BaseModel


class S3Adressing(BaseModel):
    """This adjust the S3 service to use path-based urls"""

    addressing_style: str = "path"
