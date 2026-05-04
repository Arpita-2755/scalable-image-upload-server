from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.config import Settings
from app.main import app


class FakeS3Client:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def upload_fileobj(self, file_obj, bucket: str, key: str, ExtraArgs=None) -> None:  # noqa: N803
        self.calls.append(
            {
                "bytes": file_obj.read(),
                "bucket": bucket,
                "key": key,
                "extra_args": ExtraArgs,
            }
        )


@pytest.fixture()
def client() -> tuple[TestClient, FakeS3Client]:
    fake_s3 = FakeS3Client()
    app.state.s3_client = fake_s3
    app.state.settings = Settings(
        s3_bucket_name="test-bucket",
        aws_region="us-east-1",
        s3_endpoint_url=None,
        instance_id="test-instance",
    )
    with TestClient(app) as test_client:
        yield test_client, fake_s3


def build_image_bytes(image_format: str) -> bytes:
    buffer = io.BytesIO()
    image = Image.new("RGB", (32, 32), color=(10, 20, 30))
    image.save(buffer, format=image_format)
    return buffer.getvalue()


def test_upload_png_success(client: tuple[TestClient, FakeS3Client]) -> None:
    test_client, fake_s3 = client
    files = {"file": ("sample.png", build_image_bytes("PNG"), "image/png")}

    response = test_client.post("/upload", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["url"].startswith("https://test-bucket.s3.amazonaws.com/")
    assert len(fake_s3.calls) == 1
    assert fake_s3.calls[0]["extra_args"] == {"ContentType": "image/png"}


def test_upload_jpeg_success(client: tuple[TestClient, FakeS3Client]) -> None:
    test_client, fake_s3 = client
    files = {"file": ("sample.jpg", build_image_bytes("JPEG"), "image/jpeg")}

    response = test_client.post("/upload", files=files)

    assert response.status_code == 200
    assert response.json()["url"].startswith("https://test-bucket.s3.amazonaws.com/")
    assert len(fake_s3.calls) == 1
    assert fake_s3.calls[0]["extra_args"] == {"ContentType": "image/jpeg"}


def test_reject_non_image_file(client: tuple[TestClient, FakeS3Client]) -> None:
    test_client, fake_s3 = client
    files = {"file": ("payload.txt", b"not-an-image", "text/plain")}

    response = test_client.post("/upload", files=files)

    assert response.status_code == 400
    assert response.json()["detail"] == "Only JPG/PNG image files are allowed."
    assert fake_s3.calls == []


def test_reject_file_larger_than_2mb(client: tuple[TestClient, FakeS3Client]) -> None:
    test_client, fake_s3 = client
    files = {"file": ("big.png", b"x" * (2 * 1024 * 1024 + 1), "image/png")}

    response = test_client.post("/upload", files=files)

    assert response.status_code == 413
    assert response.json()["detail"] == "File too large. Max size is 2MB."
    assert fake_s3.calls == []

