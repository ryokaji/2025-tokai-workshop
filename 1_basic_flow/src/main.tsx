import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import Passkey from "./Passkey";
import "./style.css";
const API_HOST = import.meta.env.VITE_API_HOST || "";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <>
      <h1>Passkey Demo</h1>
      <Passkey
        variant={"Registration"}
        optionsEndpoint={`${API_HOST}/generate-registration-options`}
        verifyEndpoint={`${API_HOST}/verify-registration`}
      />

      <Passkey
        variant={"Authentication"}
        optionsEndpoint={`${API_HOST}/generate-authentication-options`}
        verifyEndpoint={`${API_HOST}/verify-authentication`}
      />
    </>
  </StrictMode>
);
