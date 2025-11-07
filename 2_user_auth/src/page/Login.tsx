import { startAuthentication } from "@simplewebauthn/browser";
import React from "react";
const API_HOST = import.meta.env.VITE_API_HOST || "";

export default function Login({
  setPage,
  setLogin,
}: {
  setPage: React.Dispatch<React.SetStateAction<string>>;
  setLogin: React.Dispatch<React.SetStateAction<boolean>>;
}) {
  const [username, setUsername] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [error, setError] = React.useState("");
  const [success, setSuccess] = React.useState("");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    try {
      const res = await fetch(`${API_HOST}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
        credentials: "include",
      });
      const data = await res.json();
      if (res.ok) {
        setLogin(true);
        setSuccess("ログイン成功");
      } else {
        setLogin(false);
        setError(data.error || "ログインに失敗しました");
      }
    } catch (err) {
      setError("通信エラーが発生しました");
    }
  };

  const handleAuth = async () => {
    setError("");
    setSuccess("");

    const resp = await fetch(`${API_HOST}/generate-authentication-options`, {
      credentials: "include",
    });

    let attResp;
    try {
      const opts = await resp.json();

      attResp = await startAuthentication({ optionsJSON: opts });
    } catch (error) {
      if (
        error instanceof Error &&
        "name" in error &&
        error.name === "InvalidStateError"
      ) {
        setError(
          "Error: Authenticator was probably already registered by user"
        );
      } else if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Unknown error occurred");
      }
      throw error;
    }

    const verificationResp = await fetch(`${API_HOST}/verify-authentication`, {
      credentials: "include",
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(attResp),
    });

    const verificationJSON = await verificationResp.json();

    if (verificationJSON && verificationJSON.verified) {
      setSuccess("User authenticated!");
      setLogin(true);
    } else {
      setError(
        `Oh no, something went wrong! Response: <pre>${JSON.stringify(
          verificationJSON
        )}</pre>`
      );
    }
  };

  return (
    <>
      <ul style={{ listStyle: "none", padding: 0 }}>
        <li>
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
            <button type="submit">ログイン</button>
          </form>
        </li>
        <li>
          <button type="button" onClick={handleAuth}>
            <strong>🔐 Authenticate</strong>
          </button>
        </li>
        <li>
          <button type="button" onClick={() => setPage("home")}>
            戻る
          </button>
        </li>
      </ul>
    </>
  );
}
