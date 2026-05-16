import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import api, { getErrorMessage } from "../api";

function PostForm({ user }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditing = Boolean(id);
  const [form, setForm] = useState({ title: "", content: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(isEditing);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!isEditing) return;

    api
      .get(`/api/v1/posts/${id}/`)
      .then((response) => {
        setForm({ title: response.data.title, content: response.data.content });
        if (!response.data.can_edit) {
          setError("Only the author can edit this post.");
        }
      })
      .catch(() => setError("Could not load the post."))
      .finally(() => setLoading(false));
  }, [id, isEditing]);

  function updateField(event) {
    setForm({ ...form, [event.target.name]: event.target.value });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      const response = isEditing
        ? await api.put(`/api/v1/posts/${id}/`, form)
        : await api.post("/api/v1/posts/", form);
      navigate(`/posts/${response.data.id}`);
    } catch (err) {
      setError(getErrorMessage(err, "Could not save post."));
    } finally {
      setSubmitting(false);
    }
  }

  if (!user) {
    return (
      <main className="app-container max-w-3xl py-10">
        <div className="surface p-8 text-center">
          <h1 className="mb-2 text-2xl font-black text-[#12343b]">Login required</h1>
          <p className="mb-5 text-[#607078]">You need an account before writing posts.</p>
          <Link to="/login" className="btn btn-dark">Go to login</Link>
        </div>
      </main>
    );
  }

  if (loading) {
    return <main className="mx-auto max-w-3xl px-5 py-10 font-semibold text-[#607078]">Loading editor...</main>;
  }

  return (
    <main className="app-container max-w-3xl py-8">
      <form onSubmit={handleSubmit} className="surface p-6 md:p-8">
        <p className="mb-2 text-sm font-black uppercase tracking-[0.16em] text-[#d86f45]">Editor</p>
        <h1 className="mb-2 text-3xl font-black text-[#12343b]">{isEditing ? "Edit post" : "Create post"}</h1>
        <p className="mb-6 text-[#607078]">Share a clear title and a thoughtful story.</p>

        {error && <p className="alert-error mb-4">{error}</p>}

        <label className="mb-4 block">
          <span className="mb-2 block font-bold text-[#39545c]">Title</span>
          <input name="title" value={form.title} onChange={updateField} className="field text-lg font-bold" required />
        </label>

        <label className="mb-6 block">
          <span className="mb-2 block font-bold text-[#39545c]">Content</span>
          <textarea name="content" value={form.content} onChange={updateField} rows={12} className="field leading-7" required />
        </label>

        <div className="flex flex-wrap gap-3">
          <button disabled={submitting || Boolean(error && isEditing)} className="btn btn-primary disabled:opacity-60">
            {submitting ? "Saving..." : "Save post"}
          </button>
          <Link to={isEditing ? `/posts/${id}` : "/"} className="btn btn-ghost">
            Cancel
          </Link>
        </div>
      </form>
    </main>
  );
}

export default PostForm;
