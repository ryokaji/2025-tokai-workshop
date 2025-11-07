const API_HOST = import.meta.env.VITE_API_HOST || "";
type Props = {
  setPage: (page: string) => void;
  login: boolean;
  setLogin: (login: boolean) => void;
};

export default function Home({ setPage, login, setLogin }: Props) {
  return (
    <>
      <h1>サンプルページ</h1>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {login ? (
          <>
            <li>
              <button
                onClick={() => {
                  fetch(`${API_HOST}/logout`, { method: "POST" });
                  setLogin(false);
                }}
              >
                ログアウト
              </button>
            </li>
            <li>
              <button onClick={() => setPage("user")}>ユーザー情報</button>
            </li>
          </>
        ) : (
          <>
            <li>
              <button onClick={() => setPage("signup")}>サインアップ</button>
            </li>
            <li>
              <button onClick={() => setPage("login")}>ログイン</button>
            </li>
          </>
        )}
      </ul>
    </>
  );
}
