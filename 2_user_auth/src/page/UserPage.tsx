import { startRegistration } from "@simplewebauthn/browser";
import React, { useEffect, useState } from "react";

const API_HOST = import.meta.env.VITE_API_HOST || "";
const optionsEndpoint = `${API_HOST}/generate-registration-options`;
const verifyEndpoint = `${API_HOST}/verify-registration`;

export default function UserPage({
  setPage,
  login,
}: {
  setPage: React.Dispatch<React.SetStateAction<string>>;
  login: boolean;
}) {
  if (!login) {
    return (
      <>
        <div>ログインしてください</div>
        <button type="button" onClick={() => setPage("home")}>
          戻る
        </button>
      </>
    );
  }

  const [userInfo, setUserInfo] = useState("");
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_HOST}/users/me`, {
          credentials: "include",
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        });

        const data = await res.json();
        if (res.ok) {
          console.log("ok");
          console.log("data", data);
          setUserInfo(JSON.stringify(data, null, 2));
        } else {
          console.log("ng");
        }
      } catch (err) {
        console.log("ng");
        console.log("err", err);
      }
    })();
  }, []);

  const handleRegister = async () => {
    const resp = await fetch(optionsEndpoint, {
      credentials: "include",
    });

    let attResp;
    try {
      const opts = await resp.json();
      attResp = await startRegistration({ optionsJSON: opts });
    } catch (error) {
      if (
        error instanceof Error &&
        "name" in error &&
        error.name === "InvalidStateError"
      ) {
        alert("Error: Authenticator was probably already registered by user");
      } else if (error instanceof Error) {
        alert(error.message);
      } else {
        alert("Unknown error occurred");
      }
      // throw error;
    }

    const verificationResp = await fetch(verifyEndpoint, {
      credentials: "include",
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(attResp),
    });

    const verificationJSON = await verificationResp.json();

    if (verificationJSON && verificationJSON.verified) {
      // setSuccessMessage("Authenticator registered!");
      console.log("ok");
    } else {
      alert(
        `Oh no, something went wrong! Response: <pre>${JSON.stringify(
          verificationJSON
        )}</pre>`
      );
    }
  };

  return (
    <>
      <div>ユーザー情報</div>
      <textarea value={userInfo} readOnly />
      <button type="button" onClick={() => setPage("home")}>
        戻る
      </button>
      <button type="button" onClick={handleRegister}>
        登録
      </button>
    </>
  );
}
