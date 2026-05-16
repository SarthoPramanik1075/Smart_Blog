import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api, { getErrorMessage } from "../api";

function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    confirm_password: "",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function updateField(event) {
    setForm({ ...form, [event.target.name]: event.target.value });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      const response = await api.post("/api/auth/register/", form);
      navigate("/verify-email", {
        state: {
          email: response.data.email,
          message: response.data.detail,
        },
      });
    } catch (err) {
      setError(getErrorMessage(err, "Registration failed."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="app-container grid min-h-[calc(100vh-73px)] place-items-center py-10">
      <form onSubmit={handleSubmit} className="surface w-full max-w-md p-6 md:p-8">
        <p className="mb-2 text-sm font-black uppercase tracking-[0.16em] text-[#d86f45]">Join Smart Blog</p>
        <h1 className="mb-2 text-3xl font-black text-[#12343b]">Create account</h1>
        <p className="mb-6 text-[#607078]">Create your account, then verify your email before login.</p>

        {error && <p className="alert-error mb-4">{error}</p>}

        <label className="mb-4 block">
          <span className="mb-2 block font-bold text-[#39545c]">Username</span>
          <input name="username" value={form.username} onChange={updateField} className="field" required />
        </label>

        <label className="mb-4 block">
          <span className="mb-2 block font-bold text-[#39545c]">Email</span>
          <input name="email" type="email" value={form.email} onChange={updateField} className="field" required />
        </label>

        <label className="mb-4 block">
          <span className="mb-2 block font-bold text-[#39545c]">Password</span>
          <input name="password" type="password" value={form.password} onChange={updateField} className="field" minLength={8} required />
        </label>

        <label className="mb-6 block">
          <span className="mb-2 block font-bold text-[#39545c]">Confirm password</span>
          <input name="confirm_password" type="password" value={form.confirm_password} onChange={updateField} className="field" minLength={8} required />
        </label>

        <button disabled={submitting} className="btn btn-primary w-full disabled:opacity-60">
          {submitting ? "Sending code..." : "Register"}
        </button>

        <p className="mt-5 text-center text-sm text-[#607078]">
          Already have an account? <Link to="/login" className="font-bold text-[#d86f45]">Login</Link>
        </p>
      </form>
    </main>
  );
}

export default Register;
