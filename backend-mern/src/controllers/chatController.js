// Chat controller with RAG integration
// Calls the Python RAG service for intelligent legal answers

import os from "os";
import path from "path";
import { promises as fs } from "fs";
import mammoth from "mammoth";
import pdfParse from "pdf-parse";
import WordExtractor from "word-extractor";
import UserDocument from "../models/UserDocument.js";

const RAG_SERVICE_URL = process.env.RAG_SERVICE_URL || "http://localhost:8000";

const extractor = new WordExtractor();

async function extractTextFromFile(file) {
  const fileName = file.originalname.toLowerCase();

  if (fileName.endsWith(".pdf") || file.mimetype === "application/pdf") {
    const parsed = await pdfParse(file.buffer);
    return parsed.text || "";
  }

  if (
    fileName.endsWith(".docx") ||
    file.mimetype === "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  ) {
    const result = await mammoth.extractRawText({ buffer: file.buffer });
    return result.value || "";
  }

  if (fileName.endsWith(".doc") || file.mimetype === "application/msword") {
    const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), "legal-rag-doc-"));
    const tempFilePath = path.join(tempDir, file.originalname);

    try {
      await fs.writeFile(tempFilePath, file.buffer);
      const doc = await extractor.extract(tempFilePath);
      return doc.getBody() || "";
    } finally {
      await fs.rm(tempDir, { recursive: true, force: true });
    }
  }

  throw new Error("Unsupported file type. Please upload a PDF, DOC, or DOCX file.");
}

export const uploadDocument = async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ message: "No file uploaded" });
    }

    const userId = req.userId; // From auth middleware
    const fileName = req.file.originalname;
    const fileContent = await extractTextFromFile(req.file);

    if (!fileContent || !fileContent.trim()) {
      return res.status(400).json({
        message: "Could not extract readable text from this file.",
      });
    }

    // Send to RAG service for indexing
    try {
      const ragResponse = await fetch(`${RAG_SERVICE_URL}/upload`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: fileName,
          content: fileContent,
          user_id: userId,
        }),
      });

      if (!ragResponse.ok) {
        console.error("RAG service upload error:", ragResponse.status);
        return res.status(500).json({ 
          message: "Failed to process document in RAG service" 
        });
      }

      const ragData = await ragResponse.json();

      // Store document in MongoDB for later retrieval
      // Deactivate previous documents for this user
      await UserDocument.updateMany(
        { userId, isActive: true },
        { $set: { isActive: false } }
      );

      // Save new document as active
      const userDocument = new UserDocument({
        userId,
        title: fileName,
        content: fileContent,
        documentId: ragData.document_id,
        isActive: true,
      });
      await userDocument.save();

      res.status(200).json({
        message: "Document uploaded successfully",
        document_id: ragData.document_id,
        title: fileName,
        timestamp: new Date().toISOString(),
      });
    } catch (fetchError) {
      console.error("Error connecting to RAG service:", fetchError.message);
      res.status(503).json({ 
        message: "RAG service unavailable. Please try again later." 
      });
    }
  } catch (error) {
    console.error("Upload error:", error);
    res.status(500).json({ message: error.message || "Failed to upload document" });
  }
};

export const sendMessage = async (req, res) => {
  try {
    const { message } = req.body;
    const userId = req.userId; // From auth middleware

    if (!message || !message.trim()) {
      return res.status(400).json({ message: "Message is required" });
    }

    // Get user's active uploaded document if any
    const userDocument = await UserDocument.findOne({ userId, isActive: true });

    // Call RAG service
    try {
      const queryPayload = {
        question: message,
        top_k: 3,
        threshold: 0.3,
      };

      // Include user document if exists
      if (userDocument) {
        queryPayload.user_doc_text = userDocument.content;
        queryPayload.user_doc_title = userDocument.title;
      }

      const ragResponse = await fetch(`${RAG_SERVICE_URL}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(queryPayload),
      });

      if (!ragResponse.ok) {
        console.error("RAG service error:", ragResponse.status);
        // Fallback to placeholder if RAG service is down
        const fallbackResponse = generateFallbackResponse(message);
        return res.status(200).json({
          message: fallbackResponse,
          timestamp: new Date().toISOString(),
          source: "fallback",
        });
      }

      const ragData = await ragResponse.json();
      const topScores = Array.isArray(ragData.sources)
        ? ragData.sources.slice(0, 3).map((source) => source?.relevance_score)
        : [];

      res.status(200).json({
        message: ragData.answer,
        timestamp: new Date().toISOString(),
        source: "rag",
        rag_sources: ragData.sources,
        rag_top_scores: topScores,
      });
    } catch (fetchError) {
      console.error("Error connecting to RAG service:", fetchError.message);
      // Fallback response if RAG service is unavailable
      const fallbackResponse = generateFallbackResponse(message);
      res.status(200).json({
        message: fallbackResponse + "\n\n⚠️ Note: Using fallback mode. RAG service unavailable.",
        timestamp: new Date().toISOString(),
        source: "fallback",
      });
    }
  } catch (error) {
    console.error("Chat error:", error);
    res.status(500).json({ message: "Failed to process message" });
  }
};

// Fallback response when RAG service is unavailable
function generateFallbackResponse(userMessage) {
  const lowerMessage = userMessage.toLowerCase();

  if (lowerMessage.includes("contract") || lowerMessage.includes("agreement")) {
    return "Based on common legal practices, contracts are legally binding agreements between two or more parties. Key elements include offer, acceptance, consideration, and mutual intent. For specific contract law questions, please consult your jurisdiction's statutes.";
  }

  if (lowerMessage.includes("copyright") || lowerMessage.includes("intellectual property")) {
    return "Copyright law protects original works of authorship. The duration and specific protections vary by jurisdiction. For detailed information about copyright in your region, please refer to relevant intellectual property statutes.";
  }

  if (lowerMessage.includes("liability") || lowerMessage.includes("negligence")) {
    return "Legal liability typically requires establishing duty of care, breach, causation, and damages. Negligence standards vary by jurisdiction and case type. Consult relevant case law and statutes for your specific situation.";
  }

  return `Thank you for your legal query: "${userMessage}". I understand you're asking about legal matters. For the most accurate information, please ensure the RAG service is running or consult with a qualified attorney.`;
}
