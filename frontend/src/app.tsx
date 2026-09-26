import { Route, Routes } from "react-router-dom";

import { Layout } from "@/components/layout/layout";
import { GeneratePage } from "@/pages/generate-page";
import { Landing } from "@/pages/landing";
import { NotFound } from "@/pages/not-found";
import { RecipePage } from "@/pages/recipe-page";
import { ScanPage } from "@/pages/scan-page";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Landing />} />
        <Route path="/generar" element={<GeneratePage />} />
        <Route path="/escanear" element={<ScanPage />} />
        <Route path="/recetas/:id" element={<RecipePage />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}