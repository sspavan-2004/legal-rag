import { Link, Route, Routes } from "react-router-dom";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import OAuthCallback from "./pages/OAuthCallback";
import ChatPage from "./pages/ChatPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/oauth/google" element={<OAuthCallback />} />
      <Route path="/chat" element={<ChatPage />} />
      <Route
        path="*"
        element={
          <div className="page-center">
            <div className="card">
              <h2>Page not found</h2>
              <Link className="btn btn-primary" to="/">
                Go Home
              </Link>
            </div>
          </div>
        }
      />
    </Routes>
  );
}

export default App;
