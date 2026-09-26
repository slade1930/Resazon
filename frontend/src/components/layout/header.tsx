import { Menu, Sparkles, X } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";

import { Logo } from "@/components/shared/logo";
import { LANGS, useI18n } from "@/lib/i18n";
import { cn } from "@/lib/utils";

const NAV = [
  { to: "/", i18nKey: "nav.descubrir" },
  { to: "/generar", i18nKey: "nav.generar" },
  { to: "/escanear", i18nKey: "nav.escanear" },
];

function navItemClass({ isActive }: { isActive: boolean }) {
  return cn(
    "rounded-full px-5 py-2.5 text-[15px] font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
    isActive ? "bg-secondary text-secondary-foreground" : "text-muted-foreground hover:bg-muted hover:text-foreground",
  );
}

function LanguageSwitcher({ className }: { className?: string }) {
  const { lang, setLang } = useI18n();
  return (
    <div className={cn("inline-flex items-center gap-0.5 rounded-full border border-border bg-card p-0.5", className)}>
      {LANGS.map(({ code, label, flag }) => (
        <button
          key={code}
          type="button"
          onClick={() => setLang(code)}
          title={label}
          aria-pressed={lang === code}
          aria-label={label}
          className={cn(
            "grid size-8 place-items-center rounded-full text-xs font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
            lang === code ? "bg-marino-dark text-primary-foreground shadow-soft" : "text-muted-foreground hover:text-foreground",
          )}
        >
          <span aria-hidden>{flag}</span>
        </button>
      ))}
    </div>
  );
}

export function Header() {
  const [open, setOpen] = useState(false);
  const location = useLocation();
  const { t } = useI18n();

  useEffect(() => setOpen(false), [location.pathname]);

  return (
    <header className="sticky top-0 z-40 border-b border-border/70 bg-background/80 backdrop-blur-xl">
      <div className="mx-auto flex h-20 max-w-6xl items-center justify-between gap-4 px-5">
        <Link to="/" aria-label={t("aria.home")}>
          <Logo className="h-16" />
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {NAV.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.to === "/"} className={navItemClass}>
              {t(item.i18nKey)}
            </NavLink>
          ))}
        </nav>

        <div className="hidden items-center gap-2 md:flex">
          <LanguageSwitcher />
          <Link
            to="/generar"
            className="inline-flex h-11 items-center gap-2 rounded-full bg-marino-dark px-6 text-sm font-semibold text-primary-foreground shadow-soft transition-all hover:bg-marino focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background active:scale-[0.98]"
          >
            <Sparkles className="size-4 text-maize" />
            {t("cta.crearReceta")}
          </Link>
        </div>

        <button
          className="inline-flex size-10 items-center justify-center rounded-full border border-border bg-card focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background md:hidden"
          onClick={() => setOpen((v) => !v)}
          aria-label={open ? t("aria.closeMenu") : t("aria.openMenu")}
        >
          {open ? <X className="size-5" /> : <Menu className="size-5" />}
        </button>
      </div>

      {open && (
        <div className="border-t border-border bg-card px-5 py-4 md:hidden">
          <nav className="flex flex-col gap-1">
            {NAV.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={navItemClass}
              >
                {t(item.i18nKey)}
              </NavLink>
            ))}
            <div className="mt-2 flex items-center gap-2">
              <LanguageSwitcher className="flex-1 justify-center" />
              <Link
                to="/generar"
                className="inline-flex h-11 flex-1 items-center justify-center gap-2 rounded-full bg-marino-dark px-5 text-sm font-semibold text-primary-foreground"
              >
                <Sparkles className="size-4 text-maize" />
                {t("cta.crearReceta")}
              </Link>
            </div>
          </nav>
        </div>
      )}
    </header>
  );
}