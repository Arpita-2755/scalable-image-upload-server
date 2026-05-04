from __future__ import annotations

import io
import logging
from datetime import datetime, timezone
from uuid import uuid4

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from app.config import ALLOWED_IMAGE_FORMATS, MAX_FILE_SIZE_BYTES, Settings, load_settings

logger = logging.getLogger("image-upload")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(title="Scalable Image Upload Server", version="1.0.0")
app.state.settings = load_settings()
app.state.s3_client = None


def build_object_key(file_extension: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"{timestamp}_{uuid4().hex}.{file_extension}"


def detect_image_format(payload: bytes) -> tuple[str, str]:
    try:
        with Image.open(io.BytesIO(payload)) as image:
            image_format = (image.format or "").upper()
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG/PNG image files are allowed.",
        ) from exc

    if image_format not in ALLOWED_IMAGE_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG/PNG image files are allowed.",
        )

    file_extension, content_type = ALLOWED_IMAGE_FORMATS[image_format]
    return file_extension, content_type


def build_s3_url(bucket_name: str, object_key: str) -> str:
    return f"https://{bucket_name}.s3.amazonaws.com/{object_key}"


def create_s3_client(settings: Settings):
    return boto3.client(
        "s3",
        region_name=settings.aws_region,
        endpoint_url=settings.s3_endpoint_url,
    )


def get_s3_client():
    if app.state.s3_client is None:
        settings: Settings = app.state.settings
        app.state.s3_client = create_s3_client(settings)
    return app.state.s3_client


@app.get("/health")
def health() -> dict[str, str]:
    settings: Settings = app.state.settings
    return {"status": "ok", "instance": settings.instance_id}


@app.post("/upload")
async def upload_image(file: UploadFile = File(...)) -> dict[str, str]:
    payload = await file.read(MAX_FILE_SIZE_BYTES + 1)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty.",
        )

    if len(payload) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Max size is 2MB.",
        )

    file_extension, content_type = detect_image_format(payload)
    object_key = build_object_key(file_extension)

    settings: Settings = app.state.settings
    try:
        get_s3_client().upload_fileobj(
            io.BytesIO(payload),
            settings.s3_bucket_name,
            object_key,
            ExtraArgs={"ContentType": content_type},
        )
    except (ClientError, BotoCoreError) as exc:
        logger.exception("S3 upload failed on %s", settings.instance_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image to S3.",
        ) from exc

    image_url = build_s3_url(settings.s3_bucket_name, object_key)
    logger.info("Uploaded %s via %s", object_key, settings.instance_id)
    return {"url": image_url}
