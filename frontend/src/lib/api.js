export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV ? "http://localhost:5001/api" : "/api");

export const authRequest = async (path, payload) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000);

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    const raw = await response.text();
    const data = raw ? JSON.parse(raw) : {};

    if (!response.ok) {
      throw new Error(data.message || "Request failed");
    }

    return data;
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("Request timed out. Please try again.");
    }
    if (error instanceof SyntaxError) {
      throw new Error("Server returned invalid response");
    }
    if (error.message === "Failed to fetch") {
      throw new Error("Cannot connect to server. Please make sure backend is running on port 5001.");
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
};

export const sendMessage = async (message) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s for chat responses

  try {
    const token = localStorage.getItem("token");
    if (!token) {
      throw new Error("Authentication required");
    }

    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ message }),
      signal: controller.signal,
    });

    const raw = await response.text();
    const data = raw ? JSON.parse(raw) : {};

    if (!response.ok) {
      throw new Error(data.message || "Failed to send message");
    }

    return data;
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("Request timed out. Please try again.");
    }
    if (error instanceof SyntaxError) {
      throw new Error("Server returned invalid response");
    }
    if (error.message === "Failed to fetch") {
      throw new Error("Cannot connect to server. Please make sure backend is running.");
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
};

export const uploadDocument = async (file) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 60000); // 60s for uploads

  try {
    const token = localStorage.getItem("token");
    if (!token) {
      throw new Error("Authentication required");
    }

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/chat/upload`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
      signal: controller.signal,
    });

    const raw = await response.text();
    const data = raw ? JSON.parse(raw) : {};

    if (!response.ok) {
      throw new Error(data.message || "Failed to upload document");
    }

    return data;
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("Upload timed out. Please try again with a smaller file.");
    }
    if (error instanceof SyntaxError) {
      throw new Error("Server returned invalid response");
    }
    if (error.message === "Failed to fetch") {
      throw new Error("Cannot connect to server. Please make sure backend is running.");
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
};
