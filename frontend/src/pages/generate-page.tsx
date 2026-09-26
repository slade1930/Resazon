import { ArrowLeft, Dice5, Sparkles, Wand2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { IngredientPicker, POPULAR } from "@/components/shared/ingredient-picker";
import { RecipeView } from "@/components/recipe/recipe-view";
import { Reveal } from "@/components/shared/reveal";
import { Button } from "@/components/ui/button";
import { apiErrorMessage, errorCode, useI18n } from "@/lib/i18n";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import type { RecipeDetail } from "@/lib/types";

const GOALS = [
  { key: null, label: "goal.none", emoji: "✨" },
  { key: "mas proteinas", label: "goal.masProteinas", emoji: "💪" },
  { key: "menos sodio", label: "goal.menosSodio", emoji: "🧂" },
  { key: "bajo en grasas", label: "goal.bajoGrasas", emoji: "🥑" },
  { key: "alto en fibra", label: "goal.altoFibra", emoji: "🌾" },
  { key: "vegetariano", label: "goal.vegetariano", emoji: "🥦" },
  { key: "sin gluten", label: "goal.sinGluten", emoji: "🌽" },
];

const LOADING_LINE_KEYS = ["1", "2", "3", "4", "5", "6"];

export function GeneratePage() {
  const [params] = useSearchParams();
  const { t } = useI18n();
  const initial = useMemo(
    () => (params.get("ingredientes") ?? "").split(",").filter(Boolean).map((s) => s.trim().toLowerCase()),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  );

  const [ingredients, setIngredients] = useState<string[]>(initial);
  const [goal, setGoal] = useState<string | null>(null);
  const [recipe, setRecipe] = useState<RecipeDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errorKind, setErrorKind] = useState<"disabled" | "busy" | "generic" | null>(null);
  const [loadingLine, setLoadingLine] = useState(() => t("gen.loading1"));

  useEffect(() => {
    if (!loading) return;
    setLoadingLine(t(`gen.loading${LOADING_LINE_KEYS[Math.floor(Math.random() * LOADING_LINE_KEYS.length)]}`));
    const ix = setInterval(() => {
      setLoadingLine(t(`gen.loading${LOADING_LINE_KEYS[Math.floor(Math.random() * LOADING_LINE_KEYS.length)]}`));
    }, 2600);
    return () => clearInterval(ix);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loading, t]);

  async function run() {
    if (ingredients.length === 0) return;
    setLoading(true);
    setError(null);
    setErrorKind(null);
    setRecipe(null);
    try {
      const res = await api.generate(ingredients, goal);
      setRecipe(res.recipe);
    } catch (e) {
      const code = errorCode(e);
      setErrorKind(code === "ai_not_configured" ? "disabled" : code === "upstream_ai_error" || code === "ai_response_error" ? "busy" : "generic");
      setError(apiErrorMessage(e, t));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl px-5 py-10">
      <Link
        to="/"
        className="mb-6 inline-flex items-center gap-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
      >
        <ArrowLeft className="size-4" />
        {t("back.volver")}
      </Link>

      <Reveal>
        <div className="bg-noise relative overflow-hidden rounded-3xl border border-border bg-card p-8 shadow-soft">
          <div className="pointer-events-none absolute -right-16 -top-16 size-56 rounded-full bg-maize-soft blur-3xl" />
          <span className="inline-flex items-center gap-2 rounded-full bg-aji-soft px-3.5 py-1.5 text-xs font-semibold text-aji">
            <Wand2 className="size-3.5" />
            {t("gen.badge")}
          </span>
          <h1 className="mt-4 font-display text-4xl font-black tracking-tight">
            {t("gen.title")}
          </h1>
          <p className="mt-2 max-w-xl text-pretty text-muted-foreground">
            {t("gen.sub")}
          </p>

          <div className="mt-7">
            <IngredientPicker value={ingredients} onChange={setIngredients} />
          </div>

          <div className="mt-6">
            <p className="mb-2.5 text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
              {t("gen.goalLabel")}
            </p>
            <div className="flex flex-wrap gap-2">
              {GOALS.map((g) => (
                <button
                  key={g.key ?? "none"}
                  type="button"
                  onClick={() => setGoal(g.key)}
                  className={cn(
                    "rounded-full border px-3.5 py-2 text-sm font-medium transition-all",
                    goal === g.key
                      ? "border-transparent bg-marino-dark text-primary-foreground shadow-soft"
                      : "border-border bg-card text-secondary-foreground hover:bg-muted",
                  )}
                >
                  <span className="mr-1">{g.emoji}</span>
                  {t(g.label)}
                </button>
              ))}
            </div>
          </div>

          <div className="mt-7 flex flex-wrap items-center gap-3">
            <Button
              size="lg"
              onClick={run}
              disabled={ingredients.length === 0 || loading}
              className="rounded-full"
            >
              <Sparkles className="size-4" />
              {loading ? t("gen.loading") : t("gen.button")}
            </Button>
            <Button
              variant="outline"
              size="lg"
              className="rounded-full"
              onClick={() => {
                const shuffled = [...POPULAR].sort(() => Math.random() - 0.5);
                setIngredients(shuffled.slice(0, 3 + Math.floor(Math.random() * 3)));
              }}
              disabled={loading}
            >
              <Dice5 className="size-4" />
              {t("gen.surprise")}
            </Button>
          </div>
        </div>
      </Reveal>

      {loading && (
        <div className="bg-noise relative mt-10 overflow-hidden rounded-2xl border border-border bg-card p-10 text-center shadow-soft">
          <div className="pointer-events-none absolute -left-16 -top-20 size-64 rounded-full bg-maize-soft blur-3xl" />
          <div className="mx-auto grid size-20 animate-[spin_4s_linear_infinite] place-items-center rounded-full bg-maize-soft text-5xl shadow-soft">
            🍲
          </div>
          <p className="mt-5 font-display text-xl font-bold">{loadingLine}</p>
          <p className="mt-1 text-sm text-muted-foreground">
            {t("gen.loadingHint", { n: ingredients.length, s: ingredients.length === 1 ? "" : "s" })}
          </p>
        </div>
      )}

      {error && !loading && (
        <div className="mt-10 rounded-2xl border border-dashed border-aji/40 bg-aji-soft/40 p-8 text-center">
          <p className="font-display text-xl font-bold text-destructive">
            {errorKind === "disabled" ? t("gen.errorDisabled") : errorKind === "busy" ? t("gen.errorBusy") : t("gen.failed")}
          </p>
          <p className="mt-1 text-sm text-muted-foreground">{error}</p>
          <Button onClick={run} className="mt-5 rounded-full" disabled={ingredients.length === 0}>
            {t("gen.retry")}
          </Button>
        </div>
      )}

      {recipe && !loading && (
        <Reveal className="mt-10">
          <span className="mb-4 inline-block rounded-full bg-aji px-4 py-1.5 text-xs font-semibold uppercase tracking-widest text-primary-foreground">
            {t("gen.readyBadge")}
          </span>
          <RecipeView recipe={recipe} />
        </Reveal>
      )}
    </div>
  );
}