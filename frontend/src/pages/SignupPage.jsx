import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { API_BASE_URL, authRequest } from "../lib/api";

function SignupPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleGoogleSignup = () => {
    window.location.href = `${API_BASE_URL}/auth/google`;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setMessage("");

    if (password !== confirmPassword) {
      setMessage("Passwords do not match");
      setLoading(false);
      return;
    }

    try {
      const data = await authRequest("/auth/signup", { name, email, password });
      localStorage.setItem("token", data.token);
      setMessage("Signup successful");
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
        <p className="tag">Get Started</p>
        <h1>Sign Up</h1>
        <form className="form" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Full Name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            required
          />
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
            minLength={6}
            required
          />
          <div style={{ position: "relative" }}>
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Confirm Password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              minLength={6}
              required
              style={{ paddingRight: "2.5rem" }}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              style={{
                position: "absolute",
                right: "0.75rem",
                top: "50%",
                transform: "translateY(-50%)",
                background: "none",
                border: "none",
                cursor: "pointer",
                fontSize: "1.2rem",
                color: "#666",
                padding: 0
              }}
            >
              {showPassword ? "👁️" : "👁️‍🗨️"}
            </button>
          </div>
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Please wait..." : "Create Account"}
          </button>
        </form>
        <button className="btn btn-outline oauth-btn" type="button" onClick={handleGoogleSignup}>
          Continue with Google
        </button>
        {message && <p className="status-text">{message}</p>}
        <p className="small-text">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </section>
    </div>
  );
}

export default SignupPage;
