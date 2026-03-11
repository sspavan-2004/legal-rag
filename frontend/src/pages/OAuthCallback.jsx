import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

function OAuthCallback() {
  const [searchParams] = useSearchParams();
  const [message, setMessage] = useState("Finishing Google sign in...");
  const navigate = useNavigate();

  useEffect(() => {
    const token = searchParams.get("token");

    if (!token) {
      setMessage("Google sign in failed. Please try again.");
      return;
    }

    localStorage.setItem("token", token);
    setMessage("Signed in successfully. Redirecting...");

    const timer = setTimeout(() => navigate("/chat"), 900);
    return () => clearTimeout(timer);
  }, [navigate, searchParams]);

  return (
    <div className="page-center">
      <section className="card auth-card">
        <p className="tag">Google OAuth</p>
        <h1>{message}</h1>
      </section>
    </div>
  );
}

export default OAuthCallback;
