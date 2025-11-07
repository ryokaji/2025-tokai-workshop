import {
  startAuthentication,
  startRegistration,
} from "@simplewebauthn/browser";
import { useState } from "react";
import type { Props } from "./type";

export default function Passkey({
  variant,
  optionsEndpoint,
  verifyEndpoint,
}: Props) {
  if (variant !== "Registration" && variant !== "Authentication") {
    throw new Error(
      `Invalid argument provided to the Component, the variant is neither 'Registration' nor 'Authentication'`
    );
  }
  const [isError, setIsError] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [debugMessage, setDebugMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const printDebug = (title: string, output: string) => {
    if (debugMessage !== "") {
      setDebugMessage((prev) => prev + `\n\n// ${title}\n${output}\n`);
      return;
    } else {
      setDebugMessage(`// ${title}\n${output}\n`);
    }
  };

  const handleRegister = async () => {
    const resp = await fetch(optionsEndpoint, {
      credentials: "include",
    });

    let attResp;
    try {
      const opts = await resp.json();
      printDebug(`${variant} Options`, JSON.stringify(opts, null, 2));

      if (variant == "Registration") {
        attResp = await startRegistration({ optionsJSON: opts });
      } else if (variant == "Authentication") {
        attResp = await startAuthentication({ optionsJSON: opts });
      }

      printDebug(`${variant} Response`, JSON.stringify(attResp, null, 2));
    } catch (error) {
      if (
        error instanceof Error &&
        "name" in error &&
        error.name === "InvalidStateError"
      ) {
        setErrorMessage(
          "Error: Authenticator was probably already registered by user"
        );
      } else if (error instanceof Error) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("Unknown error occurred");
      }
      setIsSuccess(false);
      setIsError(true);
      throw error;
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
    printDebug("Server Response", JSON.stringify(verificationJSON, null, 2));

    if (verificationJSON && verificationJSON.verified) {
      if (variant == "Registration") {
        setSuccessMessage("Authenticator registered!");
      } else if (variant == "Authentication") {
        setSuccessMessage("User authenticated!");
      }
      setIsSuccess(true);
      setIsError(false);
    } else {
      setErrorMessage(
        `Oh no, something went wrong! Response: <pre>${JSON.stringify(
          verificationJSON
        )}</pre>`
      );
      setIsSuccess(false);
      setIsError(true);
    }
  };

  return (
    <section>
      <button id="btnRegBegin" onClick={handleRegister}>
        <strong>
          {variant === "Registration" ? "🚪 Register" : "🔐 Authenticate"}
        </strong>
      </button>
      {isSuccess && <p className="success">{successMessage}</p>}
      {isError && <p className="error">{errorMessage}</p>}

      <details open>
        <summary>Console</summary>
        <textarea
          className="debug"
          spellCheck="false"
          value={debugMessage}
          readOnly={true}
        ></textarea>
      </details>
    </section>
  );
}
