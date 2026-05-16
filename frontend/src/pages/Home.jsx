import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";

function Home({ user }) {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/api/v1/posts/")
      .then((response) => setPosts(response.data))
      .catch(() => setError("Could not load posts. Make sure Django is running on port 8000."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="app-container py-8">
      <section className="mb-8 grid gap-6 overflow-hidden rounded-xl bg-[#12343b] p-6 text-white shadow-2xl md:grid-cols-[1fr_auto] md:items-end md:p-8">
        <div>
          <p className="mb-3 text-sm font-bold uppercase tracking-[0.16em] text-[#f1b08a]">Community writing</p>
          <h1 className="max-w-3xl text-4xl font-black leading-tight md:text-6xl">
            Read, write, and react to thoughtful posts.
          </h1>
          <p className="mt-4 max-w-2xl text-base font-medium leading-7 text-[#d6e2e4]">
            A focused space for ideas, updates, discussions, and feedback from your community.
          </p>
        </div>
        {user ? (
          <Link to="/new" className="btn btn-primary">
            Create post
          </Link>
        ) : (
          <Link to="/login" className="btn bg-white text-[#12343b] hover:bg-[#f7eadf]">
            Login to write
          </Link>
        )}
      </section>

      {loading && <p className="font-semibold text-[#607078]">Loading posts...</p>}
      {error && <p className="alert-error">{error}</p>}
      {!loading && !error && posts.length === 0 && (
        <div className="surface p-8 text-center">
          <h2 className="text-2xl font-black text-[#12343b]">No posts yet</h2>
          <p className="mt-2 text-[#607078]">Be the first person to publish something here.</p>
        </div>
      )}

      <div className="grid gap-5">
        {posts.map((post) => (
          <article
            key={post.id}
            className="post-card p-5 md:p-6"
          >
            <div className="mb-4 flex flex-wrap items-center gap-3 text-sm font-semibold text-[#607078]">
              <span className="badge">By {post.author}</span>
              <span>{new Date(post.created_at).toLocaleString()}</span>
            </div>

            <Link to={`/posts/${post.id}`} className="block">
              <h2 className="mb-2 text-2xl font-black text-[#12343b] hover:text-[#d86f45]">{post.title}</h2>
            </Link>

            <p className="mb-4 line-clamp-3 whitespace-pre-line text-[#39545c]">{post.content}</p>

            <div className="flex flex-wrap gap-2">
              <span className="badge">Like {post.reaction_counts.like}</span>
              <span className="badge">Love {post.reaction_counts.love}</span>
              <span className="badge">Comments {post.comments.length}</span>
            </div>
          </article>
        ))}
      </div>
    </main>
  );
}

export default Home;
