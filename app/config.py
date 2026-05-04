from __future__ import annotations

import os
from dataclasses import dataclass

MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024
ALLOWED_IMAGE_FORMATS = {
    "JPEG": ("jpg", "image/jpeg"),
    "PNG": ("png", "image/png"),
}


@dataclass(frozen=True)
class Settings:
    s3_bucket_name: str
    aws_region: str
    s3_endpoint_url: str | None
    instance_id: str


def load_settings() -> Settings:
    return Settings(
        s3_bucket_name=os.getenv("S3_BUCKET_NAME", "demo-upload-bucket").strip(),
        aws_region=os.getenv("AWS_REGION", "us-east-1").strip(),
        s3_endpoint_url=os.getenv("S3_ENDPOINT_URL", "").strip() or None,
        instance_id=os.getenv("INSTANCE_ID", "unknown-instance").strip() or "unknown-instance",
    )

