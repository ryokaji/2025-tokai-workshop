import React, { useState } from "react";
const API_HOST = import.meta.env.VITE_API_HOST || "";

export default function SignUp({
  setPage,
}: {
  setPage: React.Dispatch<React.SetStateAction<string>>;
}) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    try {
      const res = await fetch(`${API_HOST}/users`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      if (res.ok) {
        setTimeout(() => {
          setPage("home");
        }, 5000);
        console.log("5秒後にログインページに遷移します");
        setSuccess("登録に成功しました");
      } else {
        setError(data.error || "登録に失敗しました");
      }
    } catch (err) {
      setError("通信エラーが発生しました");
    }
  };

  return (
    <>
      {error && <div style={{ color: "red" }}>{error}</div>}
      {success && <div style={{ color: "green" }}>{success}</div>}
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            ユーザー名:
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </label>
        </div>
        <div>
          <label>
            パスワード:
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>
        </div>
        <button type="submit">ユーザー登録</button>
      </form>
      <button type="button" onClick={() => setPage("home")}>
        戻る
      </button>
    </>
  );
}
