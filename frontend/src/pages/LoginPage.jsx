import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { API_BASE_URL, authRequest } from "../lib/api";

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleGoogleLogin = () => {
    window.location.href = `${API_BASE_URL}/auth/google`;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      const data = await authRequest("/auth/login", { email, password });
      localStorage.setItem("token", data.token);
      setMessage("Login successful");
      setTimeout(() => navigate("/chat"), 700);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-center">
      <section className="card auth-card">
        <p className="tag">Welcome Back</p>
        <h1>Login</h1>
        <form className="form" onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Please wait..." : "Login"}
          </button>
        </form>
        <button className="btn btn-outline oauth-btn" type="button" onClick={handleGoogleLogin}>
          Continue with Google
        </button>
        {message && <p className="status-text">{message}</p>}
        <p className="small-text">
          New here? <Link to="/signup">Create an account</Link>
        </p>
      </section>
    </div>
  );
}

export default LoginPage;
