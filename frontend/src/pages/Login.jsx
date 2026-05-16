import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import api, { getErrorMessage } from "../api";

function Login({ setUser }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const message = location.state?.message;

  function updateField(event) {
    setForm({ ...form, [event.target.name]: event.target.value });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      const response = await api.post("/api/auth/login/", form);
      setUser(response.data);
      navigate("/");
    } catch (err) {
      setError(getErrorMessage(err, "Login failed."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="app-container grid min-h-[calc(100vh-73px)] place-items-center py-10">
      <form onSubmit={handleSubmit} className="surface w-full max-w-md p-6 md:p-8">
        <p className="mb-2 text-sm font-black uppercase tracking-[0.16em] text-[#d86f45]">Account access</p>
        <h1 className="mb-2 text-3xl font-black text-[#12343b]">Welcome back</h1>
        <p className="mb-6 text-[#607078]">Login to publish posts, comment, and react.</p>

        {message && <p className="alert-success mb-4">{message}</p>}
        {error && <p className="alert-error mb-4">{error}</p>}

        <label className="mb-4 block">
          <span className="mb-2 block font-bold text-[#39545c]">Username</span>
          <input name="username" value={form.username} onChange={updateField} className="field" required />
        </label>

        <label className="mb-6 block">
          <span className="mb-2 block font-bold text-[#39545c]">Password</span>
          <input name="password" type="password" value={form.password} onChange={updateField} className="field" required />
        </label>

        <button disabled={submitting} className="btn btn-dark w-full disabled:opacity-60">
          {submitting ? "Logging in..." : "Login"}
        </button>

        <p className="mt-5 text-center text-sm text-[#607078]">
          New here? <Link to="/register" className="font-bold text-[#d86f45]">Create an account</Link>
        </p>
      </form>
    </main>
  );
}

export default Login;
