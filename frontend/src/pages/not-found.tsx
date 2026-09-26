import { Home } from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { useI18n } from "@/lib/i18n";

export function NotFound() {
  const { t } = useI18n();
  return (
    <div className="mx-auto flex max-w-xl flex-col items-center px-5 py-28 text-center">
      <span className="text-6xl">🫕</span>
      <h1 className="mt-6 font-display text-5xl font-black tracking-tight">
        {t("notfound.title")}
      </h1>
      <p className="mt-3 text-muted-foreground">
        {t("notfound.text")}
      </p>
      <Button asChild size="lg" className="mt-7 rounded-full">
        <Link to="/">
          <Home className="size-4" />
          {t("notfound.home")}
        </Link>
      </Button>
    </div>
  );
}