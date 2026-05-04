# Scalable Image Upload Server (No Database)

Backend system with:
- FastAPI upload API (`POST /upload`)
- AWS S3 image storage
- Two backend instances
- NGINX round-robin load balancer
- GitHub Actions CI pipeline

## Architecture

```
Client -> NGINX:80 -> app1:3001 / app2:3001 -> AWS S3
```

## Requirements

- Python 3.10+
- AWS S3 bucket
- AWS credentials with `s3:PutObject`
- (Optional for containerized run) Docker + Docker Compose

## Environment

Create `.env` from `.env.example` and set:

```env
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_SESSION_TOKEN=
S3_ENDPOINT_URL=
```

## Setup

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run Multiple Backend Instances

Terminal 1:

```bash
python run.py --port 3001 --instance backend-1
```

Terminal 2:

```bash
python run.py --port 3002 --instance backend-2
```

## NGINX Load Balancer

Use [`nginx/nginx.conf`](nginx/nginx.conf):
- listens on port `80`
- uses round-robin upstream
- enforces `client_max_body_size 2m`

If your NGINX runs directly on host machine, set upstream targets to:
- `127.0.0.1:3001`
- `127.0.0.1:3002`

If using Docker Compose, `nginx.conf` already targets `app1:3001` and `app2:3001`.

## Docker Compose (Optional)

```bash
docker compose up --build
```

This starts:
- `app1` (backend-1)
- `app2` (backend-2)
- `nginx` on `http://localhost:80`

## API

### `POST /upload`

Request:
- `multipart/form-data`
- field name: `file`
- allowed image types: JPG/PNG
- max size: 2MB

Success response:

```json
{
  "url": "https://<bucket-name>.s3.amazonaws.com/<image-name>"
}
```

### `GET /health`

Used to check liveness and instance identity for load-balance verification.

## Test with curl

Upload request:

```bash
curl -X POST http://localhost/upload \
  -F "file=@sample.png"
```

Sample response:

```json
{
  "url": "https://my-bucket.s3.amazonaws.com/20260504T120001000000Z_2c8b7f....png"
}
```

## Verify Load Balancing

- Send multiple upload requests through NGINX (`http://localhost/upload`)
- Check backend logs and confirm both instance IDs (`backend-1`, `backend-2`) receive traffic

## CI (GitHub Actions)

Workflow file: `.github/workflows/ci.yml`

On `push` and `pull_request`, pipeline will:
1. Set up Python
2. Install dependencies
3. Run test suite (`pytest`)

The workflow fails if tests fail.

## Tests

Run locally:

```bash
pytest -q
```

Coverage includes:
- valid PNG upload
- valid JPEG upload
- non-image rejection
- >2MB rejection
