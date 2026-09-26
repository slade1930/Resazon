import {
  Camera,
  ChefHat,
  Search,
  SlidersHorizontal,
  Sparkles,
  Wand2,
  X,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { IngredientPicker } from "@/components/shared/ingredient-picker";
import { Reveal } from "@/components/shared/reveal";
import { RecipeCard } from "@/components/shared/recipe-card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ImageStreamHero, type StreamImage } from "@/components/ui/image-stream-hero";
import { api } from "@/lib/api";
import { apiErrorMessage, difficultySlug, useI18n } from "@/lib/i18n";
import { recipePhotoUrl } from "@/lib/recipe-photos";
import { recipePalette } from "@/lib/recipe-visuals";
import type { RecipeSearchResponse, RecipeSummary } from "@/lib/types";

const CATALOG_SIZE = 50;

function CardSkeleton() {
  return (
    <div className="overflow-hidden rounded-2xl border border-border bg-card shadow-soft">
      <div className="bg-noise relative aspect-[16/10] overflow-hidden bg-muted">
        <span className="pointer-events-none absolute -right-4 -bottom-6 select-none text-[8rem] leading-none opacity-15">
          🍲
        </span>
      </div>
      <div className="space-y-3 p-4">
        <Skeleton className="h-5 w-3/4" />
        <Skeleton className="h-4 w-1/2" />
        <Skeleton className="h-4 w-2/3" />
      </div>
    </div>
  );
}

function ResultSkeleton() {
  return (
    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 3 }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  );
}

type DiffFilter = "facil" | "media" | "dificil" | null;

function xmlEscape(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function wrapName(name: string, max = 16): string {
  const words = name.split(/\s+/);
  const lines: string[] = [];
  let line = "";
  for (const w of words) {
    const next = line ? `${line} ${w}` : w;
    if (next.length > max && line) {
      lines.push(line);
      line = w;
    } else {
      line = next;
    }
    if (lines.length === 2) break;
  }
  if (line && lines.length < 2) lines.push(line);
  return lines.join("\n");
}

function buildStreamImages(catalog: RecipeSummary[]): StreamImage[] {
  const featured = catalog.slice(0, 12);
  return featured.map((r) => {
    const photo = recipePhotoUrl(r.name);
    const p = recipePalette(r.name);
    const nameLines = xmlEscape(wrapName(r.name)).split("\n");
    const nameText = nameLines
      .map(
        (l, i) =>
          `<text x="36" y="${556 + i * 56}" font-size="${40 - i * 6}" font-weight="900" fill="#FFFFFF">${l}</text>`,
      )
      .join("");
    const svg =
      `<svg xmlns="http://www.w3.org/2000/svg" width="480" height="640" viewBox="0 0 480 640">` +
      `<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">` +
      `<stop offset="0" stop-color="${p.to}"/><stop offset="0.55" stop-color="${p.from}"/><stop offset="1" stop-color="${p.from}"/>` +
      `</linearGradient></defs>` +
      `<rect width="480" height="640" fill="url(#g)"/>` +
      `<rect width="480" height="640" fill="#FFFFFF" opacity="0.06"/>` +
      `<rect y="470" width="480" height="170" fill="#000000" opacity="0.28"/>` +
      `<text x="240" y="330" font-size="150" text-anchor="middle">${p.emoji}</text>` +
      nameText +
      `</svg>`;
    return {
      src: photo ?? `data:image/svg+xml,${encodeURIComponent(svg)}`,
      alt: r.name,
    };
  });
}

export function Landing() {
  const [params, setParams] = useSearchParams();
  const { t, lang } = useI18n();
  const initial = useMemo(
    () => (params.get("ingredientes") ?? "").split(",").filter(Boolean).map((s) => s.trim().toLowerCase()),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  );

  const [ingredients, setIngredients] = useState<string[]>(initial);
  const [results, setResults] = useState<RecipeSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [catalog, setCatalog] = useState<RecipeSummary[]>([]);
  const [catFilter, setCatFilter] = useState<string | null>(null);
  const [diffFilter, setDiffFilter] = useState<DiffFilter>(null);
  const lastSearch = useRef<string[]>([]);

  useEffect(() => {
    api
      .listRecipes(1, CATALOG_SIZE)
      .then((data) => setCatalog(data.items))
      .catch(() => {});
  }, [lang]);

  useEffect(() => {
    if (initial.length > 0 && lastSearch.current.length === 0) {
      lastSearch.current = initial;
      void runSearch(initial);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (lastSearch.current.length > 0 && hasSearched) {
      void runSearch(lastSearch.current);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang]);

  async function runSearch(ings: string[]) {
    if (ings.length === 0) return;
    lastSearch.current = ings;
    params.delete("ingredientes");
    setParams({ ingredientes: ings.join(",") }, { replace: true });
    setLoading(true);
    setError(null);
    try {
      const res = await api.searchRecipes(ings);
      setResults(res);
      setHasSearched(true);
    } catch (e) {
      setError(apiErrorMessage(e, t));
    } finally {
      setLoading(false);
    }
  }

  const categories = useMemo(() => {
    const seen = new Set<string>();
    for (const r of catalog) {
      if (r.category) seen.add(r.category);
    }
    return [...seen].sort((a, b) => a.localeCompare(b));
  }, [catalog]);

  const filteredCatalog = useMemo(() => {
    return catalog.filter((r) => {
      if (catFilter && r.category !== catFilter) return false;
      if (diffFilter && difficultySlug(r.difficulty) !== diffFilter) return false;
      return true;
    });
  }, [catalog, catFilter, diffFilter]);

  const hasActiveFilter = catFilter !== null || diffFilter !== null;

  function chipClass(active: boolean) {
    return cn(
      "inline-flex h-9 items-center gap-1.5 rounded-full border px-3.5 text-sm font-medium transition-colors",
      active
        ? "border-transparent bg-marino-dark text-primary-foreground shadow-soft"
        : "border-border bg-card text-secondary-foreground hover:bg-muted",
    );
  }

  return (
    <>
      {/* ============ HERO: corredor de recetas, título abajo ============ */}
      <section className="relative flex min-h-[100svh] flex-col justify-end overflow-hidden lg:min-h-[96svh]">
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-background/80 via-transparent to-background/70" />

        <ImageStreamHero
          images={buildStreamImages(catalog)}
          cards={10}
          speed={24}
          axis={46}
          path={{
            perspective: 30,
            exitHeight: 44,
            railExit: 40,
            railBirth: -10,
            fan: 3.5,
          }}
          className="absolute inset-0"
        >
          <div className="pointer-events-none absolute inset-x-0 bottom-0 z-[1] h-[68%] bg-gradient-to-t from-marino-dark via-marino-dark/75 to-transparent" />

          <div className="relative z-10 mx-auto flex min-h-0 w-full max-w-6xl flex-1 flex-col justify-end px-4 pb-8 pt-24 sm:px-5 md:pb-10 lg:pb-20 lg:pt-24">
            <div className="text-center">
              <Reveal>
                <span className="inline-flex items-center gap-2 rounded-full border border-primary-foreground/20 bg-marino-dark/70 px-3 py-1 text-xs font-semibold text-maize shadow-xs backdrop-blur-sm sm:px-3.5 sm:py-1.5">
                  <span className="size-1.5 rounded-full bg-aji" />
                  {t("hero.badge")}
                </span>
              </Reveal>

              <Reveal delay={0.05}>
                <h1 className="mx-auto mt-4 max-w-3xl text-balance font-display text-4xl leading-[1.05] font-black tracking-tight text-white drop-shadow-lg sm:mt-6 sm:text-6xl lg:text-[4.15rem] lg:leading-[1.02]">
                  {t("hero.title1")}{" "}
                  <span className="underline-squiggle text-maize">{t("hero.titleAccent")}</span>
                </h1>
              </Reveal>

              <Reveal delay={0.09}>
                <p className="mt-2 flex flex-wrap items-baseline justify-center gap-x-2.5 font-hand text-xl text-white drop-shadow-md sm:mt-4 sm:text-3xl">
                  <span className="font-bold text-aji">{t("hero.slogan1")}</span>
                  <span className="font-bold text-maize">{t("hero.slogan2")}</span>
                </p>
              </Reveal>

              <Reveal delay={0.12}>
                <p className="mx-auto mt-3 max-w-2xl text-pretty text-base leading-relaxed text-white/90 drop-shadow-sm sm:mt-5 sm:text-lg">
                  {t("hero.sub")}
                </p>
              </Reveal>

              <Reveal delay={0.18}>
                <div className="mx-auto mt-4 w-full max-w-2xl rounded-t-[2rem] border border-b-0 border-primary-foreground/15 bg-background/85 p-3 shadow-lift backdrop-blur-md sm:mt-10 sm:p-6">
                  <IngredientPicker
                    value={ingredients}
                    onChange={setIngredients}
                    autoFocus
                  />
                  <div className="mt-3 flex flex-wrap items-center justify-center gap-2 sm:mt-4 sm:gap-3">
                    <Button
                      size="lg"
                      onClick={() => runSearch(ingredients)}
                      disabled={ingredients.length === 0 || loading}
                      className="rounded-full"
                    >
                      <Search className="size-4" />
                      {loading ? t("search.loading") : t("search.button")}
                    </Button>
                    <Link
                      to="/escanear"
                      className="inline-flex h-12 items-center gap-2 rounded-full border border-border bg-card px-5 text-sm font-semibold text-secondary-foreground transition-colors hover:bg-muted sm:px-6"
                    >
                      <Camera className="size-4" />
                      {t("hero.scanAlt")}
                    </Link>
                  </div>
                </div>
              </Reveal>
            </div>
          </div>
        </ImageStreamHero>
      </section>

      {/* ============ RESULTADOS ============ */}
      {hasSearched && (
        <section className="mx-auto max-w-6xl px-5 py-10">
          <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
            <div>
              <h2 className="font-display text-3xl font-bold">{t("results.title")}</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                {loading
                  ? t("results.loading")
                  : error
                    ? t("results.error")
                    : t((results?.total ?? 0) === 1 ? "results.countOne" : "results.countMany", { n: results?.total ?? 0 })}
              </p>
            </div>
            {ingredients.length > 0 && (
              <Link
                to={`/generar?ingredientes=${ingredients.join(",")}`}
                className="inline-flex items-center gap-2 rounded-full bg-marino-dark px-5 py-2.5 text-sm font-semibold text-primary-foreground transition-colors hover:bg-marino"
              >
                <Wand2 className="size-4 text-maize" />
                {t("results.generateNew")}
              </Link>
            )}
          </div>

          {loading ? (
            <ResultSkeleton />
          ) : error ? (
            <div className="rounded-2xl border border-dashed border-aji/40 bg-aji-soft/40 p-8 text-center">
              <p className="font-medium text-destructive">{error}</p>
              <p className="mt-1 text-sm text-muted-foreground">
                {t("results.apiErrorHint")}
              </p>
            </div>
          ) : results && results.recipes.length > 0 ? (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {results.recipes.map((r) => (
                <RecipeCard key={r.id ?? r.name} recipe={r} />
              ))}
            </div>
          ) : (
            <div className="rounded-2xl border border-border bg-card p-10 text-center">
              <span className="mx-auto grid size-14 place-items-center rounded-full bg-maize-soft text-2xl">
                🍳
              </span>
              <h3 className="mt-4 font-display text-2xl font-bold">
                {t("results.emptyTitle")}
              </h3>
              <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">
                {t("results.emptyText")}
              </p>
              <Link
                to={`/generar?ingredientes=${ingredients.join(",")}`}
                className="mt-5 inline-flex items-center gap-2 rounded-full bg-culantro px-6 py-3 text-sm font-semibold text-primary-foreground transition-colors hover:bg-culantro-dark"
              >
                <Sparkles className="size-4" />
                {t("results.emptyGenerate")}
              </Link>
            </div>
          )}
        </section>
      )}

      {/* ============ CÓMO FUNCIONA ============ */}
      <section className="mx-auto max-w-6xl px-5 py-16">
        <Reveal>
          <p className="text-center text-sm font-semibold uppercase tracking-[0.2em] text-culantro">
            {t("how.label")}
          </p>
          <h2 className="mt-2 text-center font-display text-4xl font-bold">
            {t("how.subtitle")}
          </h2>
        </Reveal>

        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {[
            {
              icon: <Camera className="size-5" />,
              step: "01",
              title: t("how.step1Title"),
              text: t("how.step1Text"),
              cta: { to: "/escanear", label: t("nav.escanear") },
            },
            {
              icon: <ChefHat className="size-5" />,
              step: "02",
              title: t("how.step2Title"),
              text: t("how.step2Text"),
              cta: { to: "/", label: t("nav.descubrir") },
            },
            {
              icon: <Sparkles className="size-5" />,
              step: "03",
              title: t("how.step3Title"),
              text: t("how.step3Text"),
              cta: { to: "/generar", label: t("nav.generar") },
            },
          ].map((item, i) => (
            <Reveal key={item.step} delay={i * 0.08}>
              <div className="group relative h-full overflow-hidden rounded-3xl border border-border bg-card p-7 shadow-soft transition-all duration-300 hover:-translate-y-1 hover:shadow-lift">
                <div className="flex items-start justify-between">
                  <span className="grid size-12 place-items-center rounded-2xl bg-culantro text-primary-foreground shadow-soft">
                    {item.icon}
                  </span>
                  <span className="font-display text-5xl font-black text-muted/70 transition-colors group-hover:text-maize-soft">
                    {item.step}
                  </span>
                </div>
                <h3 className="mt-5 font-display text-xl font-bold">{item.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{item.text}</p>
                <Link
                  to={item.cta.to}
                  className="mt-4 inline-flex items-center gap-1 text-sm font-semibold text-culantro transition-colors group-hover:text-aji"
                >
                  {item.cta.label}
                  <span className="transition-transform group-hover:translate-x-1">→</span>
                </Link>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ============ SHOWCASE ============ */}
      <section className="mx-auto max-w-6xl px-5 py-10">
        <Reveal>
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-culantro">
                {t("showcase.label")}
              </p>
              <h2 className="mt-2 font-display text-4xl font-bold">
                {t("showcase.title")}
              </h2>
            </div>
            <p className="max-w-sm text-sm text-muted-foreground">
              {t("showcase.text")}
            </p>
          </div>
        </Reveal>

        {(categories.length > 0 || hasActiveFilter) && (
          <div className="mt-6 flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
              <SlidersHorizontal className="size-3.5" />
              {t("filters.title")}
            </span>

            {categories.map((c) => (
              <button
                key={c}
                type="button"
                onClick={() => setCatFilter(catFilter === c ? null : c)}
                className={chipClass(catFilter === c)}
                aria-pressed={catFilter === c}
              >
                {c}
              </button>
            ))}

            {categories.length > 0 && <span className="mx-1 h-5 w-px bg-border" />}

            {(["facil", "media", "dificil"] as const).map((d) => (
              <button
                key={d}
                type="button"
                onClick={() => setDiffFilter(diffFilter === d ? null : d)}
                className={chipClass(diffFilter === d)}
                aria-pressed={diffFilter === d}
              >
                {t(`difficulty.${d}`)}
              </button>
            ))}

            {hasActiveFilter && (
              <button
                type="button"
                onClick={() => {
                  setCatFilter(null);
                  setDiffFilter(null);
                }}
                className="inline-flex h-9 items-center gap-1.5 rounded-full px-3.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
              >
                <X className="size-3.5" />
                {t("filters.clear")}
              </button>
            )}
          </div>
        )}

        <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {filteredCatalog.map((r) => (
            <RecipeCard key={r.id ?? r.name} recipe={r} />
          ))}
          {catalog.length === 0 &&
            Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="aspect-[16/10] overflow-hidden rounded-2xl border border-border bg-card shadow-soft">
                <div className="bg-noise relative size-full rounded-2xl rounded-b-none bg-muted">
                  <span className="pointer-events-none absolute inset-0 grid select-none place-items-center text-7xl opacity-15">🍳</span>
                </div>
              </div>
            ))}
        </div>
      </section>

      {/* ============ CTA FINAL ============ */}
      <section className="mx-auto max-w-6xl px-5 pt-14">
        <Reveal>
          <div className="bg-noise relative overflow-hidden rounded-3xl bg-marino-dark px-8 py-14 text-center text-primary-foreground shadow-lift sm:px-14">
            <div className="pointer-events-none absolute -left-20 -top-24 size-72 rounded-full bg-culantro/40 blur-3xl" />
            <div className="pointer-events-none absolute -bottom-24 -right-16 size-72 rounded-full bg-aji/25 blur-3xl" />
            <span className="relative inline-block text-4xl">🍽️</span>
            <h2 className="relative mx-auto mt-4 max-w-lg text-balance font-display text-4xl font-black">
              {t("final.title")}
            </h2>
            <p className="relative mx-auto mt-3 max-w-md text-primary-foreground/80">
              {t("final.text")}
            </p>
            <div className="relative mt-7 flex flex-wrap items-center justify-center gap-3">
              <Button asChild size="lg" variant="maize" className="rounded-full">
                <Link to="/generar">
                  <Sparkles className="size-4" />
                  {t("final.generate")}
                </Link>
              </Button>
              <Button
                asChild
                size="lg"
                variant="outline"
                className="rounded-full border-primary-foreground/25 bg-transparent text-primary-foreground hover:bg-primary-foreground/10"
              >
                <Link to="/escanear">
                  <Camera className="size-4" />
                  {t("final.scan")}
                </Link>
              </Button>
            </div>
          </div>
        </Reveal>
      </section>
    </>
  );
}

function cn(...parts: (string | false | null | undefined)[]) {
  return parts.filter(Boolean).join(" ");
}