import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import api, { getErrorMessage } from "../api";

const reactions = [
  ["like", "Like"],
  ["love", "Love"],
  ["funny", "Funny"],
  ["dislike", "Dislike"],
];

function PostDetail({ user }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [comment, setComment] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get(`/api/v1/posts/${id}/`)
      .then((response) => setPost(response.data))
      .catch(() => setError("Post not found."))
      .finally(() => setLoading(false));
  }, [id]);

  async function handleReaction(reactionType) {
    try {
      const response = await api.post(`/api/v1/posts/${id}/reaction/`, { reaction_type: reactionType });
      setPost(response.data);
    } catch (err) {
      setError(getErrorMessage(err, "Could not update reaction."));
    }
  }

  async function handleComment(event) {
    event.preventDefault();
    setError("");

    try {
      const response = await api.post(`/api/v1/posts/${id}/comments/`, { content: comment });
      setPost(response.data);
      setComment("");
    } catch (err) {
      setError(getErrorMessage(err, "Could not add comment."));
    }
  }

  async function handleDelete() {
    if (!window.confirm("Delete this post?")) return;

    await api.delete(`/api/v1/posts/${id}/`);
    navigate("/");
  }

  if (loading) {
    return <main className="app-container max-w-4xl py-10 font-semibold text-[#607078]">Loading post...</main>;
  }

  if (!post) {
    return <main className="app-container max-w-4xl py-10 font-semibold text-red-700">{error}</main>;
  }

  return (
    <main className="app-container max-w-4xl py-8">
      {error && <p className="alert-error mb-4">{error}</p>}

      <article className="surface p-6 md:p-8">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <p className="flex flex-wrap items-center gap-2 font-semibold text-[#607078]">
            <span className="badge">By {post.author}</span>
            <span>{new Date(post.created_at).toLocaleString()}</span>
          </p>
          {post.can_edit && (
            <div className="flex gap-2">
              <Link to={`/posts/${post.id}/edit`} className="btn btn-ghost min-h-0 py-2">
                Edit
              </Link>
              <button onClick={handleDelete} className="btn min-h-0 border border-red-200 bg-white py-2 text-red-700 hover:bg-red-50">
                Delete
              </button>
            </div>
          )}
        </div>

        <h1 className="mb-5 text-4xl font-black leading-tight text-[#12343b] md:text-5xl">{post.title}</h1>
        <p className="whitespace-pre-line text-lg leading-8 text-[#39545c]">{post.content}</p>
      </article>

      <section className="mt-5 rounded-xl border border-[#ded8ce] bg-white/70 p-5">
        <h2 className="mb-3 text-xl font-black text-[#12343b]">Reactions</h2>
        <div className="flex flex-wrap gap-2">
          {reactions.map(([key, label]) => (
            <button
              key={key}
              onClick={() => handleReaction(key)}
              disabled={!user}
              className={`btn min-h-0 border px-4 py-2 ${post.user_reaction === key ? "border-[#d86f45] bg-[#d86f45] text-white" : "border-[#c7bfb4] bg-white text-[#12343b] hover:bg-[#e9e3d8]"} disabled:cursor-not-allowed disabled:opacity-55`}
            >
              {label} {post.reaction_counts[key]}
            </button>
          ))}
        </div>
        {!user && <p className="mt-3 text-sm font-semibold text-[#607078]">Login to react.</p>}
      </section>

      <section className="py-6">
        <h2 className="mb-4 text-xl font-black text-[#12343b]">Comments</h2>

        {user ? (
          <form onSubmit={handleComment} className="mb-6 grid gap-3">
            <textarea value={comment} onChange={(event) => setComment(event.target.value)} rows={3} className="field" placeholder="Write a comment..." required />
            <button className="btn btn-dark w-fit">Add comment</button>
          </form>
        ) : (
          <p className="surface mb-6 p-4 font-semibold text-[#607078]">
            <Link to="/login" className="text-[#d86f45]">Login</Link> to join the discussion.
          </p>
        )}

        <div className="grid gap-3">
          {post.comments.length === 0 && <p className="font-semibold text-[#607078]">No comments yet.</p>}
          {post.comments.map((item) => (
            <div key={item.id} className="post-card p-4">
              <p className="mb-2 text-sm font-bold text-[#607078]">
                {item.author} · {new Date(item.created_at).toLocaleString()}
              </p>
              <p className="whitespace-pre-line text-[#39545c]">{item.content}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

export default PostDetail;
