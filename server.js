const express = require("express");
const multer = require("multer");
const AWS = require("aws-sdk");
const { v4: uuidv4 } = require("uuid");
require("dotenv").config();

const app = express();

const storage = multer.memoryStorage();

const upload = multer({
  storage,
  limits: { fileSize: 2 * 1024 * 1024 },
  fileFilter: (req, file, cb) => {
    if (file.mimetype === "image/jpeg" || file.mimetype === "image/png") {
      cb(null, true);
    } else {
      cb(new Error("Only JPG/PNG allowed"), false);
    }
  },
});

const s3 = new AWS.S3({
  accessKeyId: process.env.AWS_ACCESS_KEY,
  secretAccessKey: process.env.AWS_SECRET_KEY,
  region: process.env.AWS_REGION,
});

app.post("/upload", upload.single("image"), async (req, res) => {
  try {
    const file = req.file;

    if (!file) {
      return res.status(400).json({ error: "No file uploaded" });
    }

    const fileName = `${uuidv4()}-${Date.now()}`;

    const params = {
      Bucket: process.env.S3_BUCKET,
      Key: fileName,
      Body: file.buffer,
      ContentType: file.mimetype,
    };

    await s3.upload(params).promise();

    const url = `https://${process.env.S3_BUCKET}.s3.amazonaws.com/${fileName}`;

    res.json({ url });

  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

const PORT = process.env.PORT || 3001;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});