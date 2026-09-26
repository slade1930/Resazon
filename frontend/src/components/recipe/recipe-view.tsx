import { BadgeCheck, Check, Clock, ExternalLink, Flame, Gauge, Users } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { difficultySlug, useI18n } from "@/lib/i18n";
import { recipePhotoUrl } from "@/lib/recipe-photos";
import { coverStyle, recipePalette } from "@/lib/recipe-visuals";
import type { RecipeDetail } from "@/lib/types";

function NutritionBar({ label, value, max, color }: { label: string; value: number | null; max: number; color: string }) {
  const pct = value == null ? 0 : Math.min((value / max) * 100, 100);
  return (
    <div>
      <div className="flex items-baseline justify-between text-xs">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-semibold tabular-nums">
          {value == null ? "—" : `${Math.round(value)} g`}
        </span>
      </div>
      <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-muted">
        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  );
}

function typeLabel(recipe: RecipeDetail, t: (k: string) => string) {
  if (recipe.type === "ai_generated")
    return { text: t("view.generated"), cls: "bg-aji text-primary-foreground" };
  if (recipe.type === "ai_adapted")
    return { text: t("view.adapted"), cls: "bg-culantro text-primary-foreground" };
  if (recipe.type === "postre")
    return { text: t("card.postre"), cls: "bg-[oklch(0.5_0.15_15)] text-primary-foreground" };
  if (recipe.type === "simple")
    return { text: t("card.simple"), cls: "bg-marino-dark text-primary-foreground" };
  return { text: t("view.traditional"), cls: "bg-maize text-marino-dark" };
}

export function RecipeView({ recipe }: { recipe: RecipeDetail }) {
  const { t } = useI18n();
  const { emoji } = recipePalette(recipe.name);
  const photo = recipePhotoUrl(recipe.name);
  const difficulty = difficultySlug(recipe.difficulty);
  const type = typeLabel(recipe, t);

  return (
    <>
      <div className="relative aspect-[2.1/1] overflow-hidden rounded-3xl border border-border shadow-lift sm:aspect-[2.6/1]">
        {photo ? (
          <img src={photo} alt={recipe.name} className="absolute inset-0 size-full object-cover" />
        ) : (
          <div className="absolute inset-0" style={coverStyle(recipe.name)} />
        )}
        <div className="bg-noise absolute inset-0" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/55 via-black/10 to-transparent" />
        <span className="pointer-events-none absolute -right-6 bottom-[-3.5rem] select-none text-[13rem] leading-none opacity-20">
          {emoji}
        </span>

        <div className="absolute inset-x-0 bottom-0 flex flex-wrap items-end justify-between gap-4 p-6 sm:p-8">
          <div>
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <Badge className={type.cls}>{type.text}</Badge>
              {recipe.panama_verified && (
                <Badge className="bg-culantro text-primary-foreground">
                  <BadgeCheck className="mr-1 size-3.5" />
                  {t("card.verified")}
                </Badge>
              )}
              {difficulty && (
                <Badge variant="outline" className="bg-black/20 text-white">
                  <Gauge className="mr-1 size-3.5" />
                  {t(`difficulty.${difficulty}`)}
                </Badge>
              )}
              {recipe.category && <Badge variant="outline" className="bg-black/20 text-white">{recipe.category}</Badge>}
            </div>
            <h1 className="text-balance font-display text-4xl font-black text-white drop-shadow-sm sm:text-5xl">
              {recipe.name}
            </h1>
          </div>
          <div className="flex flex-wrap gap-3">
            {recipe.preparation_time_minutes != null && (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-white/15 px-3.5 py-1.5 text-sm font-medium text-white backdrop-blur">
                <Clock className="size-4" /> {t("card.min", { n: recipe.preparation_time_minutes })}
              </span>
            )}
            <span className="inline-flex items-center gap-1.5 rounded-full bg-white/15 px-3.5 py-1.5 text-sm font-medium text-white backdrop-blur">
              <Users className="size-4" /> {t("view.persons", { n: recipe.servings })}
            </span>
          </div>
        </div>
      </div>

      {recipe.description && (
        <p className="mt-6 text-pretty text-lg leading-relaxed text-muted-foreground">
          {recipe.description}
        </p>
      )}

      <div className="mt-8 grid gap-8 lg:grid-cols-[minmax(0,0.85fr)_1fr]">
        <div>
          <Card className="h-full">
            <div className="flex items-center justify-between p-6 pb-4">
              <h2 className="font-display text-2xl font-bold">{t("view.ingredients")}</h2>
              <span className="rounded-full bg-secondary px-3 py-1 text-xs font-semibold text-secondary-foreground">
                {t("view.items", { n: recipe.ingredients.length })}
              </span>
            </div>
            <Separator className="mx-6 w-[calc(100%-3rem)]" />
            <ul className="divide-y divide-border/70 p-6 pt-3">
              {recipe.ingredients.map((ing) => (
                <li key={ing.name} className="flex items-center gap-3 py-2.5">
                  <span className="grid size-6 shrink-0 place-items-center rounded-full border border-border bg-secondary/50">
                    <Check className="size-3.5 text-culantro" />
                  </span>
                  <div className="flex-1">
                    <span className="text-[15px] font-medium">{ing.name}</span>
                    {ing.is_optional && (
                      <span className="ml-2 text-[11px] uppercase tracking-wide text-muted-foreground">
                        {t("view.optional")}
                      </span>
                    )}
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {[ing.quantity, ing.unit].filter(Boolean).join(" ") || "—"}
                  </span>
                </li>
              ))}
            </ul>
            {recipe.nestle_products.length > 0 && (
              <div className="px-6 pb-6">
                <Separator className="mb-4" />
                <p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                  {t("view.brand")}
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {recipe.nestle_products.map((p) => (
                    <Badge key={p} variant="outline">{p}</Badge>
                  ))}
                </div>
              </div>
            )}
            {recipe.source_url && (
              <div className="px-6 pb-6">
                <Separator className="mb-4" />
                <a
                  href={recipe.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-sm font-semibold text-culantro transition-colors hover:text-aji"
                >
                  <ExternalLink className="size-4" />
                  {t("view.sourceLink")}
                </a>
              </div>
            )}
          </Card>
        </div>

        <div>
          <Card className="h-full">
            <div className="p-6 pb-4">
              <h2 className="font-display text-2xl font-bold">{t("view.preparation")}</h2>
            </div>
            <Separator className="mx-6 w-[calc(100%-3rem)]" />
            <ol className="space-y-0 p-6">
              {recipe.steps.map((step, i) => (
                <li key={i} className="relative flex gap-4 pb-7 last:pb-0">
                  {i < recipe.steps.length - 1 && (
                    <span className="absolute left-[21px] top-10 h-[calc(100%-2.25rem)] w-px bg-border" />
                  )}
                  <span className="grid size-[42px] shrink-0 place-items-center rounded-full bg-culantro font-display text-lg font-bold text-primary-foreground shadow-soft">
                    {i + 1}
                  </span>
                  <p className="pt-2 text-[15px] leading-relaxed text-pretty">{step}</p>
                </li>
              ))}
            </ol>
          </Card>
        </div>
      </div>

      {recipe.nutrition && (
        <Card className="mt-8">
          <div className="grid gap-8 p-6 sm:grid-cols-[auto_1fr] sm:items-start sm:p-8">
            <div className="flex items-center gap-2">
              <span className="grid size-11 place-items-center rounded-2xl bg-aji-soft text-aji">
                <Flame className="size-5" />
              </span>
              <div>
                <p className="text-xs text-muted-foreground">{t("view.perServing")}</p>
                <p className="font-display text-4xl font-black tabular-nums">
                  {recipe.nutrition.calories == null ? "—" : Math.round(recipe.nutrition.calories)}
                  <span className="ml-1 text-lg font-semibold text-muted-foreground">kcal</span>
                </p>
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <NutritionBar label={t("view.nutProtein")} value={recipe.nutrition.protein_g} max={40} color="#E24A2A" />
              <NutritionBar label={t("view.nutCarbs")} value={recipe.nutrition.carbs_g} max={70} color="#EFB93B" />
              <NutritionBar label={t("view.nutFat")} value={recipe.nutrition.fat_g} max={30} color="#3B82F6" />
              <NutritionBar label={t("view.nutFiber")} value={recipe.nutrition.fiber_g} max={20} color="#2E7D55" />
            </div>
          </div>
          {recipe.nutrition.disclaimer && (
            <p className="border-t border-border px-6 py-3 text-xs text-muted-foreground sm:px-8">
              {recipe.nutrition.disclaimer}
            </p>
          )}
        </Card>
      )}
    </>
  );
}