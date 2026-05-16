import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Link, NavLink, useNavigate } from "react-router-dom";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import VerifyEmail from "./pages/VerifyEmail";
import PostDetail from "./pages/PostDetail";
import PostForm from "./pages/PostForm";
import api from "./api";

function Shell({ user, setUser }) {
  const navigate = useNavigate();

  async function handleLogout() {
    await api.post("/api/auth/logout/");
    setUser(null);
    navigate("/");
  }

  return (
    <div className="app-shell">
      <nav className="glass-nav">
        <div className="app-container flex flex-wrap items-center justify-between gap-4 py-4">
          <Link to="/" className="flex items-center gap-3 text-2xl font-black tracking-tight text-[#12343b]">
            <span className="brand-mark">SB</span>
            <span>Smart Blog</span>
          </Link>

          <div className="flex flex-wrap items-center gap-2 text-sm font-semibold">
            <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? "nav-link-active" : ""}`}>
              Feed
            </NavLink>
            {user && (
              <NavLink to="/new" className={({ isActive }) => `nav-link ${isActive ? "nav-link-active" : ""}`}>
                Write
              </NavLink>
            )}

            {user ? (
              <>
                <span className="badge hidden sm:inline-flex">Hi, {user.username}</span>
                <button onClick={handleLogout} className="btn btn-ghost min-h-0 py-2">
                  Logout
                </button>
              </>
            ) : (
              <>
                <NavLink to="/login" className={({ isActive }) => `nav-link ${isActive ? "nav-link-active" : ""}`}>
                  Login
                </NavLink>
                <NavLink to="/register" className={({ isActive }) => `nav-link ${isActive ? "nav-link-active" : ""}`}>
                  Register
                </NavLink>
              </>
            )}
          </div>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<Home user={user} />} />
        <Route path="/posts/:id" element={<PostDetail user={user} />} />
        <Route path="/new" element={<PostForm user={user} />} />
        <Route path="/posts/:id/edit" element={<PostForm user={user} />} />
        <Route path="/login" element={<Login setUser={setUser} />} />
        <Route path="/register" element={<Register />} />
        <Route path="/verify-email" element={<VerifyEmail />} />
      </Routes>
    </div>
  );
}

function App() {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    api
      .get("/api/auth/me/")
      .then((response) => setUser(response.data.user))
      .finally(() => setReady(true));
  }, []);

  if (!ready) {
    return (
      <div className="grid min-h-screen place-items-center bg-[#f6f3ee] text-[#12343b]">
        <div className="surface px-6 py-5 text-lg font-black">Loading Smart Blog...</div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Shell user={user} setUser={setUser} />
    </BrowserRouter>
  );
}

export default App;
