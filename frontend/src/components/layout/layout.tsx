import { Outlet } from "react-router-dom";

import { Footer } from "@/components/layout/footer";
import { Header } from "@/components/layout/header";

export function Layout() {
  return (
    <div className="flex min-h-screen flex-col">
      <div
        aria-hidden
        className="pointer-events-none fixed inset-0 -z-[5]"
        style={{
          backgroundImage: 'url("/fondo.png")',
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundAttachment: "fixed",
          backgroundRepeat: "no-repeat",
        }}
      />
      <div
        aria-hidden
        className="pointer-events-none fixed inset-0 -z-[4] bg-background/55"
      />
      <Header />
      <main className="relative flex flex-1 flex-col">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}