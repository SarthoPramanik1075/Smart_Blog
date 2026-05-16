import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import api, { getErrorMessage } from "../api";

function VerifyEmail() {
  const navigate = useNavigate();
  const location = useLocation();
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [email, setEmail] = useState(location.state?.email || "");
  const message = location.state?.message;

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      await api.post("/api/auth/verify-email/", { code, email });
      navigate("/login", {
        state: {
          message: "Email verified successfully. Please login now.",
        },
      });
    } catch (err) {
      setError(getErrorMessage(err, "Verification failed."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="app-container grid min-h-[calc(100vh-73px)] place-items-center py-10">
      <form onSubmit={handleSubmit} className="surface w-full max-w-md p-6 md:p-8">
        <p className="mb-2 text-sm font-black uppercase tracking-[0.16em] text-[#d86f45]">One more step</p>
        <h1 className="mb-2 text-3xl font-black text-[#12343b]">Verify email</h1>
        <p className="mb-6 text-[#607078]">
          {message || "Enter the email and verification code from registration."}
        </p>

        {error && <p className="alert-error mb-4">{error}</p>}

        <label className="mb-4 block">
          <span className="mb-2 block font-bold text-[#39545c]">Email</span>
          <input
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="field"
            type="email"
            required
          />
        </label>

        <label className="mb-6 block">
          <span className="mb-2 block font-bold text-[#39545c]">Verification code</span>
          <input
            value={code}
            onChange={(event) => setCode(event.target.value)}
            className="field text-center text-2xl font-black tracking-[0.3em]"
            inputMode="numeric"
            maxLength={6}
            required
          />
        </label>

        <button disabled={submitting} className="btn btn-primary w-full disabled:opacity-60">
          {submitting ? "Verifying..." : "Verify account"}
        </button>

        <p className="mt-5 text-center text-sm text-[#607078]">
          Need a new code? <Link to="/register" className="font-bold text-[#d86f45]">Register again</Link>
        </p>
      </form>
    </main>
  );
}

export default VerifyEmail;
