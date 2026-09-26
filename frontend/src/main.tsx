import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { Toaster } from "sonner";

import App from "@/app";
import { I18nProvider } from "@/lib/i18n";
import "@/index.css";

createRoot(document.getElementById("root")!).render(
  <BrowserRouter>
    <I18nProvider>
      <App />
    <Toaster
      position="top-center"
      toastOptions={{
        className: "!font-sans !rounded-2xl !border-border !bg-card !shadow-lift",
      }}
    />
    </I18nProvider>
  </BrowserRouter>,
);