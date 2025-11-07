import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import Front from "./Front.tsx";
import "./style.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Front />
  </StrictMode>
);
