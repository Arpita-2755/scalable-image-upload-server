# Scalable Image Upload Server (No Database)

## 🚀 Overview

This project implements a scalable backend system that:

* Uploads images (JPG/PNG) to AWS S3
* Supports multiple backend instances
* Uses NGINX for load balancing
* Includes CI pipeline (GitHub Actions)
* No database is used

---

## 🧱 Architecture

Client → NGINX → Multiple Backend Servers → AWS S3

---

## ⚙️ Tech Stack

* Node.js (Express)
* AWS S3
* NGINX
* GitHub Actions

---

## ✅ Progress

* [x] Project setup
* [x] Backend API created (/upload)
* [x] AWS S3 integration configured
* [x] Environment variables setup
* [x] Multiple backend instances running locally
* [ ] NGINX load balancing
* [ ] EC2 deployment
* [ ] CI pipeline

---

## 📂 Project Structure

```
image-upload-server/
│── server.js
│── .env
│── package.json
│── .gitignore
│── README.md
```

---

## 🔌 API Endpoint

### POST /upload

* Accepts: multipart/form-data
* Field name: image
* Max size: 2MB
* Allowed types: JPG, PNG

### Response

```json
{
  "url": "https://<bucket-name>.s3.amazonaws.com/<image-name>"
}
```

---

## ▶️ Run Locally

```bash
npm install
node server.js
```

---

## 🔁 Run Multiple Instances

```bash
set PORT=3001 && node server.js
set PORT=3002 && node server.js
```

---

## 📌 Notes

* No database used
* File names are generated using UUID + timestamp
* AWS credentials stored in `.env` (not committed)

---

## 🚧 Status

Work in progress — deployment coming next
