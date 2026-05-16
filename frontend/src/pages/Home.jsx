import { useEffect, useState } from "react";
import axios from "axios";

function Home() {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/api/posts/")
      .then((response) => setPosts(response.data))
      .catch((error) => console.error(error));
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      <h1 className="text-4xl font-bold mb-8">Smart Blog</h1>

      <div className="grid gap-6">
        {posts.map((post) => (
          <div
            key={post.id}
            className="bg-white rounded-2xl shadow p-6"
          >
            <h2 className="text-2xl font-semibold mb-2">
              {post.title}
            </h2>

            <p className="text-gray-700 mb-4">
              {post.content}
            </p>

            <p className="text-sm text-gray-500">
              By {post.author}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Home;