import { ArrowLeft,  ChevronRight, Leaf, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { RecipeView } from "@/components/recipe/recipe-view";
import { Reveal } from "@/components/shared/reveal";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import { apiErrorMessage, useI18n } from "@/lib/i18n";
import type { RecipeDetail } from "@/lib/types";

export function RecipePage() {
  const { id } = useParams();
  const { t, lang } = useI18n();
  const [recipe, setRecipe] = useState<RecipeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [workingHealthy, setWorkingHealthy] = useState(false);
  const [healthy, setHealthy] = useState<RecipeDetail | null>(null);

  useEffect(() => {
    window.scrollTo({ top: 0 });
    setLoading(true);
    setError(null);
    setHealthy(null);
    api
      .getRecipe(id!)
      .then(setRecipe)
      .catch((e) => setError(apiErrorMessage(e, t)))
      .finally(() => setLoading(false));
  }, [id, lang]);

  async function adaptToHealthy() {
    if (!recipe) return;
    setWorkingHealthy(true);
try {
        const res = await api.healthy(recipe.ingredients.map((i) => i.name));
        setHealthy(res.recipe);
        window.scrollTo({ top: 0, behavior: "smooth" });
      } catch (e) {
        alert(apiErrorMessage(e, t));
      } finally {
      setWorkingHealthy(false);
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-5 py-8">
      <Link
        to="/"
        className="mb-6 inline-flex items-center gap-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
      >
        <ArrowLeft className="size-4" />
        {t("recipe.back")}
      </Link>

      {loading && (
        <div className="space-y-6">
          <div className="relative overflow-hidden rounded-3xl border border-border bg-card shadow-lift">
            <span className="pointer-events-none absolute -right-6 -bottom-10 select-none text-[10rem] leading-none opacity-10">
              🍴
            </span>
            <Skeleton className="aspect-[2.6/1] rounded-3xl rounded-b-none" />
          </div>
          <div className="grid gap-8 lg:grid-cols-2">
            <Skeleton className="h-96 rounded-2xl" />
            <Skeleton className="h-96 rounded-2xl" />
          </div>
        </div>
      )}

      {error && !loading && (
        <div className="rounded-3xl border border-dashed border-aji/40 bg-aji-soft/40 p-10 text-center">
          <p className="font-display text-2xl font-bold">{t("recipe.notFound")}</p>
          {t("recipe.notFound") !== error && <p className="mt-2 text-sm text-muted-foreground">{error}</p>}
          <Button asChild className="mt-5 rounded-full">
            <Link to="/">{t("recipe.backHome")}</Link>
          </Button>
        </div>
      )}

      {recipe && !loading && (
        <>
          <Reveal>
            <RecipeView recipe={recipe} />
          </Reveal>

          {recipe.type === "traditional" && (
            <div className="mt-8 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-culantro/25 bg-culantro/8 p-6">
              <div className="flex items-center gap-4">
                <span className="grid size-12 shrink-0 place-items-center rounded-2xl bg-culantro text-primary-foreground shadow-soft">
                  <Leaf className="size-5" />
                </span>
                <div>
                  <p className="font-display text-lg font-bold">{t("recipe.healthyTitle")}</p>
                  <p className="text-sm text-muted-foreground">
                    {t("recipe.healthyText", { name: recipe.name })}
                  </p>
                </div>
              </div>
              <Button variant="default" size="lg" onClick={adaptToHealthy} disabled={workingHealthy} className="rounded-full">
                <Sparkles className="size-4" />
                {workingHealthy ? t("recipe.reinventing") : t("recipe.healthyBtn")}
              </Button>
            </div>
          )}

          {healthy && (
            <Reveal>
              <div className="mt-10">
                <div className="mb-4 flex items-center gap-3">
                  <span className="rounded-full bg-culantro px-4 py-1.5 text-xs font-semibold uppercase tracking-widest text-primary-foreground">
                    {t("recipe.adaptedBadge")}
                  </span>
                  <span className="text-sm text-muted-foreground">
                    {t("recipe.adaptedHint", { name: recipe.name })}
                  </span>
                </div>
                <RecipeView recipe={healthy} />
              </div>
            </Reveal>
          )}

          <div className="mt-10 flex items-center justify-between rounded-2xl border border-border bg-card px-6 py-5">
            <div className="flex items-center gap-3">
              <span className="font-hand text-2xl text-culantro-dark">{t("recipe.liked")}</span>
            </div>
            <Button asChild variant="outline" className="rounded-full">
              <Link to="/">
                {t("recipe.exploreMore")}
                <ChevronRight className="size-4" />
              </Link>
            </Button>
          </div>
        </>
      )}
    </div>
  );
}