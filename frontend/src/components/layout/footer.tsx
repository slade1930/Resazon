import { Instagram, Mail, MapPin, Youtube } from "lucide-react";
import { Link } from "react-router-dom";

import { Logo } from "@/components/shared/logo";
import { useI18n } from "@/lib/i18n";

export function Footer() {
  const { t } = useI18n();
  return (
    <footer className="bg-noise relative mt-24 overflow-hidden bg-marino-dark text-primary-foreground">
      <div className="pointer-events-none absolute -right-24 -top-24 size-72 rounded-full bg-culantro/30 blur-3xl" />
      <div className="pointer-events-none absolute -left-16 bottom-0 size-72 rounded-full bg-aji/15 blur-3xl" />

      <div className="relative mx-auto grid max-w-6xl gap-10 px-5 py-14 md:grid-cols-[1.4fr_1fr_1fr]">
        <div className="space-y-4">
          <Logo onLight={false} />
          <p className="max-w-xs text-sm leading-relaxed text-primary-foreground/75">
            {t("footer.tagline")}
          </p>
          <p className="font-hand text-2xl text-maize">
            {t("hero.slogan1")}{" "}
            <span className="text-primary-foreground/90">{t("hero.slogan2")}</span>
          </p>
          <div className="flex items-center gap-2 pt-1">
            <span className="inline-flex size-9 items-center justify-center rounded-full bg-primary-foreground/10 transition-colors hover:bg-primary-foreground/20">
              <Instagram className="size-4" />
            </span>
            <span className="inline-flex size-9 items-center justify-center rounded-full bg-primary-foreground/10 transition-colors hover:bg-primary-foreground/20">
              <Youtube className="size-4" />
            </span>
            <span className="inline-flex size-9 items-center justify-center rounded-full bg-primary-foreground/10 transition-colors hover:bg-primary-foreground/20">
              <Mail className="size-4" />
            </span>
          </div>
        </div>

        <div className="space-y-3">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-maize">
            {t("footer.explore")}
          </p>
          <ul className="space-y-2 text-sm text-primary-foreground/80">
            <li><Link className="hover:text-white" to="/">{t("footer.discover")}</Link></li>
            <li><Link className="hover:text-white" to="/generar">{t("footer.generate")}</Link></li>
            <li><Link className="hover:text-white" to="/escanear">{t("footer.scan")}</Link></li>
          </ul>
        </div>

        <div className="space-y-3">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-maize">
            {t("footer.about")}
          </p>
          <ul className="space-y-2 text-sm text-primary-foreground/80">
            <li className="flex items-center gap-2">
              <MapPin className="size-4 text-maize" />
              {t("footer.made")}
            </li>
            <li className="flex items-center gap-2">
              <span className="inline-block">{t("footer.recetario")}</span>
            </li>
          </ul>
        </div>
      </div>

      <div className="relative border-t border-primary-foreground/10 px-5 py-5">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 text-xs text-primary-foreground/55 sm:flex-row sm:items-center sm:justify-between">
          <p>{t("footer.disclaimer", { year: new Date().getFullYear() })}</p>
          <p className="font-hand text-base text-maize">{t("footer.enjoy")}</p>
        </div>
      </div>
    </footer>
  );
}