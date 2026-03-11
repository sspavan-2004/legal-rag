import express from "express";
import multer from "multer";
import { sendMessage, uploadDocument } from "../controllers/chatController.js";
import authMiddleware from "../middleware/authMiddleware.js";

const router = express.Router();

const allowedMimeTypes = new Set([
  "application/pdf",
  "application/msword",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "application/octet-stream",
]);

const allowedExtensions = [".pdf", ".doc", ".docx"];

// Configure multer for memory storage
const upload = multer({ 
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 15 * 1024 * 1024, // 15MB limit
  },
  fileFilter: (req, file, cb) => {
    const lowerName = file.originalname.toLowerCase();
    const hasAllowedExtension = allowedExtensions.some((ext) => lowerName.endsWith(ext));
    const hasAllowedMimeType = allowedMimeTypes.has(file.mimetype);

    if (hasAllowedExtension || hasAllowedMimeType) {
      cb(null, true);
    } else {
      cb(new Error("Only .pdf, .doc, and .docx files are allowed"));
    }
  }
});

router.post("/", authMiddleware, sendMessage);
router.post("/upload", authMiddleware, upload.single('file'), uploadDocument);

export default router;
