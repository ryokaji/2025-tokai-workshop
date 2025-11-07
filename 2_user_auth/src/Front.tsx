import { useState } from "react";
import Home from "./page/Home";
import Login from "./page/Login";
import SignUp from "./page/SignUp";
import UserPage from "./page/UserPage";

const Front = () => {
  const [page, setPage] = useState("home");
  const [login, setLogin] = useState(false);
  return (
    <>
      {page === "home" && (
        <Home setPage={setPage} login={login} setLogin={setLogin} />
      )}
      {page === "signup" && <SignUp setPage={setPage} />}
      {page === "login" && <Login setPage={setPage} setLogin={setLogin} />}
      {page === "user" && <UserPage setPage={setPage} login={login} />}
    </>
  );
};

export default Front;
