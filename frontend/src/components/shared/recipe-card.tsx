import { BadgeCheck, Clock, Gauge, Leaf, Users } from "lucide-react";
import { Link } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { difficultySlug, useI18n } from "@/lib/i18n";
import { recipePhotoUrl } from "@/lib/recipe-photos";
import { coverStyle, recipePalette } from "@/lib/recipe-visuals";
import type { RecipeSummary } from "@/lib/types";

function MatchRing({ value }: { value: number }) {
  const r = 21;
  const c = 2 * Math.PI * r;
  const filled = (Math.min(value, 100) / 100) * c;
  return (
    <div className="relative grid size-12 shrink-0 place-items-center rounded-full bg-card shadow-soft">
      <svg viewBox="0 0 48 48" className="absolute inset-0 size-full -rotate-90">
        <circle cx="24" cy="24" r={r} fill="none" strokeWidth="4" className="stroke-muted" />
        <circle
          cx="24"
          cy="24"
          r={r}
          fill="none"
          strokeWidth="4"
          strokeLinecap="round"
          stroke="#E24A2A"
          strokeDasharray={`${filled} ${c}`}
        />
      </svg>
      <span className="text-[11px] font-bold tabular-nums text-foreground">
        {Math.round(value)}%
      </span>
    </div>
  );
}

function typeLabel(type: string, t: (k: string) => string) {
  if (type === "ai_generated") return { label: t("card.ai"), emoji: "✨" };
  if (type === "ai_adapted") return { label: t("card.healthy"), emoji: "🌿" };
  if (type === "simple") return { label: t("card.simple"), emoji: "👩‍🍳" };
  if (type === "postre") return { label: t("card.postre"), emoji: "🍰" };
  return { label: t("card.traditional"), emoji: "🍳" };
}

export function RecipeCard({ recipe }: { recipe: RecipeSummary }) {
  const { t } = useI18n();
  const { emoji } = recipePalette(recipe.name);
  const photo = recipePhotoUrl(recipe.name);
  const difficulty = difficultySlug(recipe.difficulty);
  const type = typeLabel(recipe.type, t);
  const inner = (
    <Card className="group h-full overflow-hidden transition-all duration-300 hover:-translate-y-1.5 hover:shadow-lift">
      <div className="relative aspect-[16/10] overflow-hidden" style={photo ? undefined : coverStyle(recipe.name)}>
        {photo && (
          <img
            src={photo}
            alt={recipe.name}
            loading="lazy"
            className="absolute inset-0 size-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
        )}
        <div className="bg-noise absolute inset-0" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/25 via-transparent to-transparent" />

        <span className="pointer-events-none absolute -right-4 -bottom-6 select-none text-[8rem] leading-none opacity-25 transition-transform duration-500 group-hover:scale-110 group-hover:-rotate-6">
          {emoji}
        </span>

        <div className="absolute left-3.5 top-3.5 flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-card/85 px-3 py-1 text-xs font-semibold text-foreground backdrop-blur">
            <span>{type.emoji}</span>
            {type.label}
          </span>
          {recipe.panama_verified && (
            <span
              className="inline-flex items-center gap-1 rounded-full bg-culantro/90 px-2.5 py-1 text-xs font-semibold text-white backdrop-blur"
              title={t("card.verified")}
            >
              <BadgeCheck className="size-3.5" />
              <span className="hidden sm:inline">{t("card.verified")}</span>
            </span>
          )}
        </div>

        <div className="absolute right-3.5 top-3.5">
          <MatchRing value={recipe.match_percentage} />
        </div>

        <span className="absolute bottom-3.5 left-4 font-display text-2xl font-bold leading-none text-white drop-shadow-sm">
          {recipe.name}
        </span>
      </div>

      <div className="flex flex-col gap-3.5 p-4">
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
          {recipe.preparation_time_minutes != null && (
            <span className="inline-flex items-center gap-1.5">
              <Clock className="size-3.5" />
              {t("card.min", { n: recipe.preparation_time_minutes })}
            </span>
          )}
          <span className="inline-flex items-center gap-1.5">
            <Users className="size-3.5" />
            {t("card.persons", { n: recipe.servings })}
          </span>
          {difficulty && (
            <span className="inline-flex items-center gap-1.5">
              <Gauge className="size-3.5" />
              {t(`difficulty.${difficulty}`)}
            </span>
          )}
          {recipe.match_percentage > 0 && (
            <span className="inline-flex items-center gap-1.5 text-culantro-dark">
              <Leaf className="size-3.5" />
              {t("card.available", { n: recipe.available_ingredients.length })}
            </span>
          )}
        </div>

        {recipe.available_ingredients.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {recipe.available_ingredients.slice(0, 4).map((ing) => (
              <Badge key={ing} variant="success" className="text-[11px]">
                {ing}
              </Badge>
            ))}
            {recipe.available_ingredients.length > 4 && (
              <Badge variant="outline" className="text-[11px]">
                {t("card.plusMore", { n: recipe.available_ingredients.length - 4 })}
              </Badge>
            )}
          </div>
        )}

        {recipe.match_percentage === 0 && recipe.missing_ingredients.length > 0 && (
          <p className="text-xs text-muted-foreground">
            {t("card.missing", { list: recipe.missing_ingredients.slice(0, 5).join(", ") })}
            {recipe.missing_ingredients.length > 5 && (
              <> {t("card.andMore", { n: recipe.missing_ingredients.length - 5 })}</>
            )}
          </p>
        )}

        <span className="mt-auto inline-flex items-center gap-1 text-sm font-semibold text-culantro transition-colors group-hover:text-aji">
          {t("card.view")}
          <span className="transition-transform group-hover:translate-x-1">→</span>
        </span>
      </div>
    </Card>
  );

  if (recipe.id != null) {
    return (
      <Link to={`/recetas/${recipe.id}`} className="block h-full">
        {inner}
      </Link>
    );
  }
  return <div className="block h-full">{inner}</div>;
}