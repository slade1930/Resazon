import { useCallback, useRef, useState } from "react";
import { Link } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Reveal } from "@/components/shared/reveal";
import { apiErrorMessage, useI18n } from "@/lib/i18n";
import { api } from "@/lib/api";
import type { DetectedIngredient, RecipeSummary, RecipeDetail } from "@/lib/types";

import {
  ArrowLeft,
  Camera,
  ImagePlus,
  Loader2,
  Search,
  Sparkles,
  Trash2,
  X,
  Utensils,
  Leaf,
  Heart,
  ChevronLeft,
} from "lucide-react";

type RecipeType = "traditional" | "healthy";

interface ScanResults {
  scanId: number;
  detectedIngredients: DetectedIngredient[];
  recipeType: RecipeType;
  traditionalRecipes?: RecipeSummary[];
  healthyRecipe?: RecipeDetail;
}

function confidenceTone(c: number, t: (k: string) => string) {
  if (c >= 0.8) return { label: t("conf.high"), cls: "bg-culantro/15 text-culantro-dark" };
  if (c >= 0.5) return { label: t("conf.medium"), cls: "bg-maize-soft text-[oklch(0.45_0.1_75)]" };
  return { label: t("conf.low"), cls: "bg-muted text-muted-foreground" };
}

function formatPercent(n: number): string {
  return `${Math.round(n)}%`;
}

function TraditionalRecipeCard({ recipe, t }: { recipe: RecipeSummary; t: (k: string, vars?: Record<string, string | number>) => string }) {
  return (
    <Link key={recipe.id ?? recipe.name} to={`/recetas/${recipe.id}`}>
      <Card className="h-full overflow-hidden transition-all hover:-translate-y-1 hover:shadow-lift">
        <div className="relative aspect-[16/10] overflow-hidden bg-muted">
          <div className="absolute inset-0 flex items-center justify-center text-4xl">🍲</div>
        </div>
        <CardContent className="p-4 space-y-2">
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            {recipe.category && (
              <Badge variant="outline" className="text-[10px]">{recipe.category}</Badge>
            )}
            {recipe.difficulty && (
              <Badge variant="outline" className="text-[10px]">{t(`difficulty.${recipe.difficulty}`)}</Badge>
            )}
            <span className="flex items-center gap-1 text-culantro-dark font-medium">
              <Heart className="size-3" />
              {formatPercent(recipe.match_percentage)}
            </span>
          </div>
          <h3 className="font-display text-lg font-bold line-clamp-2">{recipe.name}</h3>
          <p className="text-sm text-muted-foreground line-clamp-2">
            {recipe.missing_ingredients.length > 0
              ? t("card.missing", { list: recipe.missing_ingredients.slice(0, 3).join(", ") })
              : t("card.available", { n: recipe.available_ingredients.length })}
          </p>
          <div className="flex items-center justify-between pt-2">
            <Button variant="ghost" size="sm" className="rounded-full text-culantro">
              <Search className="size-3 mr-1" />
              {t("scan.viewRecipe")}
            </Button>
            <span className="text-xs text-muted-foreground">{recipe.servings} {t("card.persons", { n: recipe.servings })}</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

function HealthyRecipeView({ recipe, t }: { recipe: RecipeDetail; t: (k: string, vars?: Record<string, string | number>) => string }) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-2xl font-bold">{t("scan.healthyTitle")}</h2>
        <p className="text-sm text-muted-foreground">{t("scan.healthySub")}</p>
      </div>

      <Card className="overflow-hidden">
        <div className="relative aspect-[16/10] overflow-hidden bg-gradient-to-br from-aji/20 to-culantro/20">
          <div className="absolute inset-0 flex items-center justify-center text-6xl">🥗</div>
          <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/70 to-transparent">
            <h3 className="font-display text-2xl font-bold text-white">{recipe.name}</h3>
          </div>
        </div>
        <CardContent className="p-6 space-y-4">
          <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
            <Badge variant="outline">{t("scan.perServing", { n: recipe.servings })}</Badge>
            <Badge variant="outline">{recipe.preparation_time_minutes} min</Badge>
          </div>

          <div className="rounded-xl bg-aji-soft/30 p-4">
            <h4 className="font-semibold mb-3">{t("scan.healthyNutrition")}</h4>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <div className="text-center">
                <p className="font-display text-2xl font-bold text-aji">{recipe.nutrition?.calories ?? "—"}</p>
                <p className="text-xs text-muted-foreground">{t("scan.calories")}</p>
              </div>
              <div className="text-center">
                <p className="font-display text-2xl font-bold text-culantro">{recipe.nutrition?.protein_g ?? "—"}g</p>
                <p className="text-xs text-muted-foreground">{t("scan.protein")}</p>
              </div>
              <div className="text-center">
                <p className="font-display text-2xl font-bold text-maize">{recipe.nutrition?.carbs_g ?? "—"}g</p>
                <p className="text-xs text-muted-foreground">{t("scan.carbs")}</p>
              </div>
              <div className="text-center">
                <p className="font-display text-2xl font-bold text-blue-500">{recipe.nutrition?.fat_g ?? "—"}g</p>
                <p className="text-xs text-muted-foreground">{t("scan.fat")}</p>
              </div>
            </div>
            <p className="mt-2 text-xs text-muted-foreground text-center">{t("scan.estimated")}</p>
          </div>

          <div>
            <h4 className="font-semibold mb-2">{t("view.ingredients")}</h4>
            <div className="flex flex-wrap gap-1.5">
              {recipe.ingredients.map((ing) => (
                <Badge key={ing.name} variant="secondary" className="text-[11px]">
                  {ing.name}
                  {ing.quantity && ` ${ing.quantity}`}
                  {ing.unit && ` ${ing.unit}`}
                </Badge>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-2">{t("view.preparation")}</h4>
            <ol className="space-y-2">
              {recipe.steps.map((step, i) => (
                <li key={i} className="flex gap-3 text-sm">
                  <span className="grid size-6 shrink-0 place-items-center rounded-full bg-culantro text-primary-foreground font-semibold">
                    {i + 1}
                  </span>
                  <p className="pt-1 leading-relaxed">{step}</p>
                </li>
              ))}
            </ol>
          </div>

          {recipe.health_notes && recipe.health_notes.length > 0 && (
            <div className="rounded-xl bg-culantro/10 p-4">
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                <Heart className="size-4 text-aji" /> Consejos saludables
              </h4>
              <ul className="space-y-1 text-sm text-muted-foreground">
                {recipe.health_notes.map((note, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="text-aji">•</span> {note}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="pt-4 border-t border-border">
            <Link to={`/recetas/${0}`}>
              <Button size="lg" className="w-full rounded-full bg-aji" variant="default">
                <Heart className="size-4 mr-2" /> {t("scan.viewRecipe")}
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export function ScanPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [detecting, setDetecting] = useState(false);
  const [recipeType, setRecipeType] = useState<RecipeType>("traditional");
  const [results, setResults] = useState<ScanResults | null>(null);
  const [error, setError] = useState<string | null>(null);

  const inputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);

  const { t: tRaw } = useI18n();
  const t = tRaw as (key: string, vars?: Record<string, string | number>) => string;

  const startCamera = useCallback(async () => {
    setCameraError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setCameraActive(true);
    } catch (e) {
      setCameraError(t("scan.permissionDenied"));
      if ((e as DOMException).name === "NotFoundError" || (e as DOMException).name === "OverconstrainedError") {
        setCameraError(t("scan.cameraNotAvailable"));
      }
    }
  }, [t]);

  const stopCamera = useCallback(() => {
    if (videoRef.current?.srcObject) {
      (videoRef.current.srcObject as MediaStream).getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
  }, []);

  const takePhoto = useCallback(() => {
    if (!videoRef.current) return;
    const canvas = document.createElement("canvas");
    const video = videoRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], "camera-photo.jpg", { type: "image/jpeg" });
          onFile(file);
          stopCamera();
        }
      }, "image/jpeg", 0.9);
    }
  }, [stopCamera]);

  function onFile(next: File | null) {
    if (!next) return;
    if (!next.type.startsWith("image/")) {
      setError(t("scan.onlyImages"));
      return;
    }
    setError(null);
    setCameraError(null);
    setFile(next);
    setResults(null);
    setRecipeType("traditional");
    setPreview(URL.createObjectURL(next));
    if (cameraActive) stopCamera();
  }

  async function detect() {
    if (!file || detecting) return;
    setDetecting(true);
    setError(null);
    try {
      const res = await api.scan(file);
      const detected = res.detected_ingredients;
      setResults({
        scanId: res.scan_id,
        detectedIngredients: detected,
        recipeType,
        traditionalRecipes: undefined,
        healthyRecipe: undefined,
      });
    } catch (e) {
      const err = e as { code?: string; message?: string };
      if (err.code === "rate_limit_exceeded") {
        setError(t("scan.rateLimitError"));
      } else {
        setError(apiErrorMessage(e, t));
      }
      setResults(null);
    } finally {
      setDetecting(false);
    }
  }

  async function changeRecipeType(newType: RecipeType) {
    if (!results || newType === results.recipeType) return;
    setRecipeType(newType);
    const baseResults = { ...results, recipeType: newType };

    if (newType === "traditional") {
      if (!baseResults.traditionalRecipes) {
        const names = baseResults.detectedIngredients.map((d) => d.name);
        try {
          const res = await api.searchRecipes(names, baseResults.scanId);
          baseResults.traditionalRecipes = res.recipes;
        } catch {
          baseResults.traditionalRecipes = [];
        }
      }
    } else {
      if (!baseResults.healthyRecipe) {
        const names = baseResults.detectedIngredients.map((d) => d.name);
        try {
          const res = await api.healthy(names);
          baseResults.healthyRecipe = res.recipe;
        } catch {
          baseResults.healthyRecipe = undefined;
        }
      }
    }
    setResults(baseResults);
  }

  // --- Renderizado por estados ---
  const showCamera = !file && !results && !detecting;
  const showTypeSelector = file && !results && !detecting;
  const showResults = !!results;

  return (
    <div className="mx-auto max-w-3xl px-5 py-10">
      <Link to="/" className="mb-6 inline-flex items-center gap-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground">
        <ArrowLeft className="size-4" /> {t("back.volver")}
      </Link>

      <Reveal>
        <span className="inline-flex items-center gap-2 rounded-full bg-culantro/12 px-3.5 py-1.5 text-xs font-semibold text-culantro-dark">
          <Camera className="size-3.5" /> {t("scan.badge")}
        </span>
        <h1 className="mt-4 font-display text-4xl font-black tracking-tight">{t("scan.title")}</h1>
        <p className="mt-2 max-w-lg text-pretty text-muted-foreground">{t("scan.sub")}</p>

        {/* Paso 1: Cámara o Archivo */}
        {showCamera && (
          <div className="mt-8 space-y-4">
            <p className="text-center text-sm text-muted-foreground">{t("scan.chooseType")}</p>
            <div className="grid gap-4 sm:grid-cols-2">
              <Button variant="outline" size="lg" className="rounded-2xl h-28 flex flex-col items-center gap-2" onClick={startCamera} disabled={cameraActive || !navigator.mediaDevices?.getUserMedia}>
                <Camera className="size-7" />
                <span className="font-medium">{t("scan.camera")}</span>
                <span className="text-xs text-muted-foreground">{t("scan.cameraHint")}</span>
              </Button>
              <Button variant="outline" size="lg" className="rounded-2xl h-28 flex flex-col items-center gap-2" onClick={() => inputRef.current?.click()}>
                <ImagePlus className="size-7" />
                <span className="font-medium">{t("scan.upload")}</span>
                <span className="text-xs text-muted-foreground">{t("scan.uploadHint")}</span>
              </Button>
            </div>
            <input ref={inputRef} type="file" accept="image/*" capture="environment" className="hidden" onChange={(e) => onFile(e.target.files?.[0] ?? null)} />
            {cameraError && <div className="rounded-xl border border-dashed border-aji/40 bg-aji-soft/40 p-4 text-center text-sm text-destructive">{cameraError}</div>}
          </div>
        )}

        {/* Cámara activa */}
        {cameraActive && (
          <div className="mt-8 space-y-4">
            <div className="relative rounded-2xl overflow-hidden bg-black">
              <video ref={videoRef} className="w-full max-h-[60vh] object-cover" autoPlay playsInline />
              <div className="absolute inset-0 flex flex-col items-center justify-between p-4">
                <p className="text-white/80 text-sm text-center">{t("scan.cameraHint")}</p>
                <div className="flex gap-3">
                  <Button variant="outline" size="lg" className="rounded-full bg-white/10 text-white border-white/20 hover:bg-white/20" onClick={stopCamera}>
                    <X className="size-4" />
                    <span>{t("scan.changePhoto")}</span>
                  </Button>
                  <Button size="lg" className="rounded-full" onClick={takePhoto}>
                    <Camera className="size-4 mr-2" /> {t("scan.analyze")}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Vista previa + Selector tipo */}
        {showTypeSelector && (
          <div className="mt-8 space-y-6">
            <div className="relative rounded-2xl overflow-hidden">
<img src={preview!} alt={t("scan.previewAlt")} className="mx-auto max-h-[26rem] w-full object-cover" />
              <button onClick={(e) => { e.stopPropagation(); setFile(null); setPreview(null); }} className="absolute right-3 top-3 grid size-9 place-items-center rounded-full bg-marino-dark/80 text-white backdrop-blur transition-colors hover:bg-aji" aria-label={t("scan.removeImage")}>
                <Trash2 className="size-4" />
              </button>
            </div>
            <div className="rounded-2xl border border-border bg-card p-6">
              <h2 className="font-display text-xl font-bold text-center mb-4">{t("scan.chooseType")}</h2>
              <div className="grid gap-3 sm:grid-cols-2">
                <Button variant={recipeType === "traditional" ? "default" : "outline"} size="lg" className="rounded-xl h-28 flex flex-col items-center gap-3 text-left" onClick={() => setRecipeType("traditional")}>
                  <div className="flex items-center gap-2"><span className="text-3xl">🇵🇦</span><div><p className="font-semibold">{t("scan.typeTraditional")}</p><p className="text-xs text-muted-foreground">{t("scan.typeTraditionalDesc")}</p></div></div>
                  <Utensils className="size-5 text-culantro" />
                </Button>
                <Button variant={recipeType === "healthy" ? "default" : "outline"} size="lg" className="rounded-xl h-28 flex flex-col items-center gap-3 text-left" onClick={() => setRecipeType("healthy")}>
                  <div className="flex items-center gap-2"><span className="text-3xl">🥗</span><div><p className="font-semibold">{t("scan.typeHealthy")}</p><p className="text-xs text-muted-foreground">{t("scan.typeHealthyDesc")}</p></div></div>
                  <Leaf className="size-5 text-aji" />
                </Button>
              </div>
            </div>
            <Button size="lg" className="w-full rounded-full" onClick={detect} disabled={detecting}>
              {detecting ? (<><Loader2 className="size-4 animate-spin mr-2" />{t("scan.analyzing")}</>) : (<><Sparkles className="size-4 mr-2" />{t("scan.analyze")}</>)}
            </Button>
          </div>
        )}

        {/* Vista previa imagen subida */}
        {file && preview && !cameraActive && !showTypeSelector && !showResults && !detecting && (
          <div className="mt-8 relative rounded-2xl overflow-hidden">
            <img src={preview!} alt={t("scan.previewAlt")} className="mx-auto max-h-[26rem] w-full object-cover" />
            <button onClick={(e) => { e.stopPropagation(); setFile(null); setPreview(null); }} className="absolute right-3 top-3 grid size-9 place-items-center rounded-full bg-marino-dark/80 text-white backdrop-blur transition-colors hover:bg-aji" aria-label={t("scan.removeImage")}><Trash2 className="size-4" /></button>
          </div>
        )}

        {/* Errores */}
        {error && (
          <div className="mt-5 rounded-2xl border border-dashed border-aji/40 bg-aji-soft/40 p-5 text-center">
            <p className="text-sm font-medium text-destructive">{error}</p>
            {file && !results && <Button variant="outline" className="mt-3 rounded-full" onClick={() => onFile(file)}>{t("scan.retryPhoto")}</Button>}
            {results && <Button variant="outline" className="mt-3 rounded-full" onClick={detect}>{t("scan.retryPhoto")}</Button>}
          </div>
        )}

        {/* Detectando - botón antes de análisis */}
        {file && !results && !showTypeSelector && !detecting && !cameraActive && (
          <div className="mt-6 flex flex-wrap items-center gap-3 justify-center">
            <Button size="lg" onClick={detect} disabled={detecting} className="rounded-full">
              {detecting ? (<><Loader2 className="size-4 animate-spin mr-2" />{t("scan.detecting")}</>) : (<><Sparkles className="size-4 mr-2" />{t("scan.analyze")}</>)}
            </Button>
            <span className="text-sm text-muted-foreground self-center">{t("scan.geminiHint")}</span>
          </div>
        )}

        {/* Detectando (loading) */}
        {detecting && (
          <div className="mt-8 flex flex-col items-center gap-4">
            <div className="mx-auto grid size-20 place-items-center rounded-full bg-maize-soft text-5xl animate-pulse">🍲</div>
            <p className="font-display text-xl font-bold">{t("scan.analyzing")}</p>
            <p className="text-sm text-muted-foreground">{t("scan.geminiHint")}</p>
          </div>
        )}

        {/* RESULTADOS */}
        {showResults && results && (
          <div className="mt-8 space-y-6">
            {/* Ingredientes detectados */}
            <div className="rounded-2xl border border-border bg-card p-4">
              <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                <h2 className="font-display text-xl font-bold">{t("scan.resultsTitle")}</h2>
                <Button variant="ghost" size="sm" onClick={() => { setFile(null); setPreview(null); setResults(null); }}>
                  <ChevronLeft className="size-4 mr-1" /> {t("scan.changePhoto")}
                </Button>
              </div>
              <div className="flex flex-wrap gap-2">
                {results.detectedIngredients.map((d) => (
                  <Badge key={d.name} variant={confidenceTone(d.confidence, t).cls.includes("culantro") ? "success" : confidenceTone(d.confidence, t).cls.includes("maize") ? "secondary" : "outline"} className="gap-1.5 py-1.5 px-3 text-sm">
                    <span className="rounded-full px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide bg-culantro/20 text-culantro-dark">{confidenceTone(d.confidence, t).label}</span> {d.name}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Selector tipo en resultados */}
            <div className="flex gap-2">
              <Button variant={recipeType === "traditional" ? "default" : "outline"} className="flex-1 rounded-xl py-3 flex items-center justify-center gap-2" onClick={() => changeRecipeType("traditional")} disabled={results.recipeType === "traditional"}>
                <Utensils className="size-4" /> <span>{t("scan.typeTraditional")}</span>
              </Button>
              <Button variant={recipeType === "healthy" ? "default" : "outline"} className="flex-1 rounded-xl py-3 flex items-center justify-center gap-2" onClick={() => changeRecipeType("healthy")} disabled={results.recipeType === "healthy"}>
                <Leaf className="size-4" /> <span>{t("scan.typeHealthy")}</span>
              </Button>
            </div>

            {/* Resultados Tradicionales */}
            {recipeType === "traditional" && (
              <div className="space-y-4">
                <h2 className="font-display text-2xl font-bold">{t("scan.traditionalTitle")}</h2>
                <p className="text-sm text-muted-foreground">{t("scan.traditionalSub")}</p>

                {results.traditionalRecipes === undefined ? (
                  <div className="flex justify-center py-8"><Loader2 className="size-8 animate-spin text-culantro" /></div>
                ) : results.traditionalRecipes && results.traditionalRecipes.length > 0 ? (
                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {results.traditionalRecipes.map((recipe) => <TraditionalRecipeCard key={recipe.id ?? recipe.name} recipe={recipe} t={t} />)}
                  </div>
                ) : (
                  <div className="rounded-2xl border border-border bg-card p-8 text-center">
                    <span className="mx-auto grid size-14 place-items-center rounded-full bg-maize-soft text-2xl">🍳</span>
                    <h3 className="mt-4 font-display text-xl font-bold">{t("results.emptyTitle")}</h3>
                    <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">{t("results.emptyText")}</p>
                    <Button asChild className="mt-5 rounded-full bg-culantro" onClick={() => changeRecipeType("healthy")}>
                      <Link to={`/generar?ingredientes=${results.detectedIngredients.map((d) => d.name).join(",")}`}>
                        <Sparkles className="size-4 mr-2" /> {t("results.emptyGenerate")}
                      </Link>
                    </Button>
                  </div>
                )}
              </div>
            )}

            {/* Resultados Saludables */}
            {recipeType === "healthy" && (
              <div className="space-y-4">
                {results.healthyRecipe === undefined && results.recipeType === "healthy" ? (
                  <div className="flex justify-center py-8"><Loader2 className="size-8 animate-spin text-aji" /></div>
                ) : results.healthyRecipe ? (
                  <HealthyRecipeView recipe={results.healthyRecipe} t={t} />
                ) : (
                  <div className="rounded-2xl border border-dashed border-aji/40 bg-aji-soft/40 p-8 text-center">
                    <p className="font-display text-xl font-bold text-destructive">{t("scan.error")}</p>
                    <Button variant="outline" className="mt-4 rounded-full" onClick={() => changeRecipeType("healthy")}>{t("scan.retryPhoto")}</Button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </Reveal>
    </div>
  );
}