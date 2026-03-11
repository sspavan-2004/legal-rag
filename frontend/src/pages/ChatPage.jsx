import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { sendMessage, uploadDocument } from "../lib/api";

function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
    }
  }, [navigate]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const lowerName = file.name.toLowerCase();
    const validExtensions = [".pdf", ".doc", ".docx"];
    const validMimeTypes = [
      "application/pdf",
      "application/msword",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/octet-stream",
    ];

    const hasValidExtension = validExtensions.some((ext) => lowerName.endsWith(ext));
    const hasValidMimeType = validMimeTypes.includes(file.type);

    if (!hasValidExtension && !hasValidMimeType) {
      setError("Please upload only .pdf, .doc, or .docx files");
      return;
    }

    // Validate file size (max 15MB)
    if (file.size > 15 * 1024 * 1024) {
      setError("File size must be less than 15MB");
      return;
    }

    setIsUploading(true);
    setError("");

    try {
      await uploadDocument(file);

      // Add system message
      const systemMessage = {
        id: Date.now(),
        text: `📄 Document "${file.name}" uploaded successfully! You can now ask questions about it.`,
        sender: "system",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, systemMessage]);

      // Clear file input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (err) {
      setError(err.message || "Failed to upload document");
    } finally {
      setIsUploading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: input,
      sender: "user",
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setError("");

    try {
      const response = await sendMessage(input);
      const topScores = Array.isArray(response.rag_top_scores)
        ? response.rag_top_scores
        : Array.isArray(response.rag_sources)
        ? response.rag_sources.slice(0, 3).map((source) => source?.relevance_score)
        : [];

      const botMessage = {
        id: Date.now() + 1,
        text: response.message,
        sender: "bot",
        timestamp: new Date().toISOString(),
        topScores,
        source: response.source,
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setError(err.message || "Failed to send message");
      // Remove the user message if request failed
      setMessages((prev) => prev.filter((msg) => msg.id !== userMessage.id));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <header className="chat-header">
        <div className="chat-header-content">
          <h1>Legal Query Assistant</h1>
          <button className="btn btn-outline btn-sm" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <div className="chat-empty-icon">⚖️</div>
            <h2>Welcome to Legal Query RAG</h2>
            <p>Ask any legal question and get precise, grounded answers.</p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`message ${
              msg.sender === "user" 
                ? "message-user" 
                : msg.sender === "system"
                ? "message-system"
                : "message-bot"
            }`}
          >
            <div className="message-content">
              <p>{msg.text}</p>
              {msg.sender === "bot" && (
                <span className="message-scores">
                  {msg.topScores?.length
                    ? `Top 3 scores: ${msg.topScores
                        .map((score) => Number(score).toFixed(3))
                        .join(", ")}`
                    : "Top 3 scores: N/A"}
                </span>
              )}
              <span className="message-time">
                {new Date(msg.timestamp).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message message-bot">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="chat-error">
          <span>⚠️ {error}</span>
        </div>
      )}

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={handleFileUpload}
          disabled={isUploading || isLoading}
          style={{ display: "none" }}
        />
        <button
          type="button"
          className="btn btn-outline btn-sm"
          disabled={isUploading || isLoading}
          onClick={() => fileInputRef.current?.click()}
          title="Upload PDF or Word document"
        >
          {isUploading ? "Uploading..." : "Upload"}
        </button>
        <input
          type="text"
          className="chat-input"
          placeholder="Ask a legal question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
        />
        <button
          type="submit"
          className="btn btn-primary"
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? "Sending..." : "Send"}
        </button>
      </form>
    </div>
  );
}

export default ChatPage;
