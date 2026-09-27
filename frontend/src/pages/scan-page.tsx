import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Reveal } from "@/components/shared/reveal";
import { apiErrorMessage, useI18n } from "@/lib/i18n";
import { api } from "@/lib/api";
import type {
  DetectedIngredient,
  RecipeSummary,
  RecipeDetail,
  RecipeIngredient,
  NutritionFacts,
} from "@/lib/types";

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

/** Redimensiona la imagen a máx 1280px en su lado mayor y la convierte a JPEG para reducir costos/tokens. */
function optimizeImage(file: File): Promise<File> {
  return new Promise((resolve) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      const MAX = 1280;
      const longest = Math.max(img.width, img.height);
      const scale = Math.min(1, MAX / longest);
      if (scale >= 1) {
        URL.revokeObjectURL(url);
        resolve(file);
        return;
      }
      const canvas = document.createElement("canvas");
      canvas.width = Math.round(img.width * scale);
      canvas.height = Math.round(img.height * scale);
      const ctx = canvas.getContext("2d");
      if (!ctx) {
        URL.revokeObjectURL(url);
        resolve(file);
        return;
      }
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      canvas.toBlob(
        (blob) => {
          URL.revokeObjectURL(url);
          if (blob) {
            const name = file.name.replace(/\.[^.]+$/, "") || "photo";
            resolve(new File([blob], `${name}.jpg`, { type: "image/jpeg" }));
          } else {
            resolve(file);
          }
        },
        "image/jpeg",
        0.85,
      );
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      resolve(file);
    };
    img.src = url;
  });
}

/** Descarta los ingredientes con confianza baja. */
function confidentIngredients(list: DetectedIngredient[]): DetectedIngredient[] {
  return list.filter((d) => d.confidence >= 0.5);
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
        <div className="relative aspect-[16/10] w-full overflow-hidden bg-muted">
          <div className="absolute inset-0 flex items-center justify-center text-4xl">🍲</div>
        </div>
        <CardContent className="space-y-2 p-4">
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            {recipe.category && <Badge variant="outline" className="text-[10px]">{recipe.category}</Badge>}
            {recipe.difficulty && <Badge variant="outline" className="text-[10px]">{t(`difficulty.${recipe.difficulty}`)}</Badge>}
            <span className="flex items-center gap-1 font-medium text-culantro-dark">
              <Heart className="size-3" />
              {formatPercent(recipe.match_percentage)}
            </span>
          </div>
          <h3 className="line-clamp-2 font-display text-lg font-bold">{recipe.name}</h3>
          <p className="line-clamp-2 text-sm text-muted-foreground">
            {recipe.missing_ingredients.length > 0
              ? t("card.missing", { list: recipe.missing_ingredients.slice(0, 3).join(", ") })
              : t("card.available", { n: recipe.available_ingredients.length })}
          </p>
          <div className="flex items-center justify-between pt-2">
            <Button variant="ghost" size="sm" className="rounded-full text-culantro">
              <Search className="mr-1 size-3" />
              {t("scan.viewRecipe")}
            </Button>
            <span className="text-xs text-muted-foreground">{recipe.servings} {t("card.persons", { n: recipe.servings })}</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

function NutritionGrid({ nutrition, t }: { nutrition: NutritionFacts | null; t: (k: string, vars?: Record<string, string | number>) => string }) {
  const items: { label: string; value: string; cls: string }[] = [
    { label: t("scan.calories"), value: `${nutrition?.calories ?? "—"}`, cls: "text-aji" },
    { label: t("scan.protein"), value: `${nutrition?.protein_g ?? "—"}g`, cls: "text-culantro" },
    { label: t("scan.carbs"), value: `${nutrition?.carbs_g ?? "—"}g`, cls: "text-maize" },
    { label: t("scan.fat"), value: `${nutrition?.fat_g ?? "—"}g`, cls: "text-blue-500" },
  ];
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {items.map((it) => (
        <div key={it.label} className="text-center">
          <p className={`font-display text-2xl font-bold ${it.cls}`}>{it.value}</p>
          <p className="text-xs text-muted-foreground">{it.label}</p>
        </div>
      ))}
    </div>
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
        <div className="relative aspect-[16/10] w-full overflow-hidden bg-gradient-to-br from-aji/20 to-culantro/20">
          <div className="absolute inset-0 flex items-center justify-center text-6xl">🥗</div>
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4">
            <h3 className="font-display text-2xl font-bold text-white">{recipe.name}</h3>
          </div>
        </div>
        <CardContent className="space-y-4 p-4 sm:p-6">
          <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
            <Badge variant="outline">{t("scan.perServing", { n: recipe.servings })}</Badge>
            {recipe.preparation_time_minutes != null && <Badge variant="outline">{recipe.preparation_time_minutes} min</Badge>}
          </div>

          <div className="rounded-xl bg-aji-soft/30 p-4">
            <h4 className="mb-3 font-semibold">{t("scan.healthyNutrition")}</h4>
            <NutritionGrid nutrition={recipe.nutrition ?? null} t={t} />
            <p className="mt-2 text-center text-xs text-muted-foreground">{t("scan.estimated")}</p>
          </div>

          <div>
            <h4 className="mb-2 font-semibold">{t("view.ingredients")}</h4>
            <div className="flex flex-wrap gap-1.5">
              {recipe.ingredients.map((ing: RecipeIngredient) => (
                <Badge key={`${ing.name}-${ing.quantity ?? ""}`} variant="secondary" className="text-[11px]">
                  {ing.name}
                  {ing.quantity ? ` ${ing.quantity}` : ""}
                  {ing.unit ? ` ${ing.unit}` : ""}
                </Badge>
              ))}
            </div>
          </div>

          <div>
            <h4 className="mb-2 font-semibold">{t("view.preparation")}</h4>
            <ol className="space-y-2">
              {recipe.steps.map((step, i) => (
                <li key={i} className="flex gap-3 text-sm">
                  <span className="grid size-6 shrink-0 place-items-center rounded-full bg-culantro font-semibold text-primary-foreground">
                    {i + 1}
                  </span>
                  <p className="pt-1 leading-relaxed">{step}</p>
                </li>
              ))}
            </ol>
          </div>

          {recipe.health_notes && recipe.health_notes.length > 0 && (
            <div className="rounded-xl bg-culantro/10 p-4">
              <h4 className="mb-2 flex items-center gap-2 font-semibold">
                <Heart className="size-4 text-aji" /> {t("scan.healthTips")}
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
        </CardContent>
      </Card>
    </div>
  );
}

export function ScanPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [detecting, setDetecting] = useState(false);
  const [typeBusy, setTypeBusy] = useState(false);
  const [recipeType, setRecipeType] = useState<RecipeType>("traditional");
  const [results, setResults] = useState<ScanResults | null>(null);
  const [error, setError] = useState<string | null>(null);

  const inputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [cameraLoading, setCameraLoading] = useState(false);
  const busyRef = useRef(false);

  const { t: tRaw } = useI18n();
  const t = tRaw as (key: string, vars?: Record<string, string | number>) => string;

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
  }, []);

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const startCamera = useCallback(async () => {
    setCameraError(null);
    setCameraLoading(true);
    try {
      let stream: MediaStream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } },
          audio: false,
        });
      } catch {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { width: { ideal: 1280 }, height: { ideal: 720 } },
          audio: false,
        });
      }
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.muted = true;
        await videoRef.current.play();
      }
      setCameraActive(true);
    } catch (e) {
      const err = e as DOMException;
      if (err.name === "NotFoundError" || err.name === "OverconstrainedError") {
        setCameraError(t("scan.cameraNotAvailable"));
      } else if (err.name === "NotAllowedError") {
        setCameraError(t("scan.permissionDenied"));
      } else {
        setCameraError(t("scan.cameraNotAvailable"));
      }
    } finally {
      setCameraLoading(false);
    }
  }, [t]);

  const takePhoto = useCallback(() => {
    const video = videoRef.current;
    if (!video || !video.videoWidth || !video.videoHeight) return;

    const MAX = 1280;
    const scale = Math.min(1, MAX / Math.max(video.videoWidth, video.videoHeight));
    const canvas = document.createElement("canvas");
    canvas.width = Math.round(video.videoWidth * scale);
    canvas.height = Math.round(video.videoHeight * scale);
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(
      async (blob) => {
        if (blob) {
          const photo = new File([blob], "camera-photo.jpg", { type: "image/jpeg" });
          await onFile(photo);
          stopCamera();
        }
      },
      "image/jpeg",
      0.85,
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stopCamera]);

  async function onFile(next: File | null) {
    if (!next) return;
    if (!next.type.startsWith("image/")) {
      setError(t("scan.onlyImages"));
      return;
    }
    try {
      const optimized = await optimizeImage(next);
      const url = URL.createObjectURL(optimized);
      if (preview) URL.revokeObjectURL(preview);
      setError(null);
      setCameraError(null);
      setFile(optimized);
      setResults(null);
      setRecipeType("traditional");
      setPreview(url);
      if (cameraActive) stopCamera();
    } catch {
      setError(t("scan.loadFailed"));
    }
  }

  function clearFile() {
    if (preview) URL.revokeObjectURL(preview);
    setFile(null);
    setPreview(null);
    setResults(null);
    setError(null);
    setCameraError(null);
  }

  async function fetchHealthy(names: string[], scanId: number): Promise<RecipeDetail | undefined> {
    const res = await api.healthy(names, scanId);
    return res.recipe;
  }

  async function detect() {
    if (!file || detecting || busyRef.current) return;
    busyRef.current = true;
    setDetecting(true);
    setError(null);
    try {
      const res = await api.scan(file);
      const detected = confidentIngredients(res.detected_ingredients);

      if (detected.length === 0) {
        setResults(null);
        setError(t("scan.noFood"));
        return;
      }

      const base: ScanResults = {
        scanId: res.scan_id,
        detectedIngredients: detected,
        recipeType,
        traditionalRecipes: res.traditional_recipes,
        healthyRecipe: undefined,
      };

      if (recipeType === "healthy") {
        try {
          base.healthyRecipe = await fetchHealthy(detected.map((d) => d.name), res.scan_id);
        } catch (e) {
          base.recipeType = "traditional";
          setRecipeType("traditional");
          setError(rateLimitMessage(e, t) ?? t("scan.error"));
        }
      }
      setResults(base);
    } catch (e) {
      setResults(null);
      setError(rateLimitMessage(e, t) ?? apiErrorMessage(e, t));
    } finally {
      setDetecting(false);
      busyRef.current = false;
    }
  }

  async function changeRecipeType(newType: RecipeType) {
    if (!results || busyRef.current) return;
    if (newType === results.recipeType) return;
    busyRef.current = true;
    setTypeBusy(true);
    setError(null);
    const previous = results.recipeType;
    setRecipeType(newType);
    const next = { ...results, recipeType: newType };
    try {
      const names = results.detectedIngredients.map((d) => d.name);
      if (newType === "traditional" && !next.traditionalRecipes) {
        const res = await api.searchRecipes(names, results.scanId);
        next.traditionalRecipes = res.recipes;
      } else if (newType === "healthy" && !next.healthyRecipe) {
        const res = await api.healthy(names, results.scanId);
        next.healthyRecipe = res.recipe;
      }
      setResults(next);
    } catch (e) {
      setRecipeType(previous);
      setError(rateLimitMessage(e, t) ?? t("scan.error"));
    } finally {
      setTypeBusy(false);
      busyRef.current = false;
    }
  }

  const showCamera = !file && !results && !detecting;
  const showTypeSelector = file && !results && !detecting;
  const showResults = !!results;

  return (
    <div className="mx-auto w-full max-w-3xl px-4 py-6 sm:px-5 sm:py-10">
      <Link to="/" className="mb-6 inline-flex items-center gap-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground">
        <ArrowLeft className="size-4" /> {t("back.volver")}
      </Link>

      <Reveal>
        <span className="inline-flex items-center gap-2 rounded-full bg-culantro/12 px-3.5 py-1.5 text-xs font-semibold text-culantro-dark">
          <Camera className="size-3.5" /> {t("scan.badge")}
        </span>
        <h1 className="mt-4 font-display text-3xl font-black tracking-tight sm:text-4xl">{t("scan.title")}</h1>
        <p className="mt-2 max-w-lg text-pretty text-sm text-muted-foreground sm:text-base">{t("scan.sub")}</p>

        {showCamera && (
          <div className="mt-6 space-y-4 sm:mt-8">
            <p className="text-center text-sm text-muted-foreground">{t("scan.chooseType")}</p>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 sm:gap-4">
              <Button
                variant="outline"
                size="lg"
                className="flex h-24 w-full flex-col items-center justify-center gap-1.5 rounded-2xl sm:h-28"
                onClick={startCamera}
                disabled={cameraLoading || !navigator.mediaDevices?.getUserMedia}
              >
                {cameraLoading ? <Loader2 className="size-6 animate-spin" /> : <Camera className="size-6 sm:size-7" />}
                <span className="text-sm font-medium sm:text-base">{t("scan.camera")}</span>
                <span className="text-center text-[11px] text-muted-foreground sm:text-xs">{t("scan.cameraHint")}</span>
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="flex h-24 w-full flex-col items-center justify-center gap-1.5 rounded-2xl sm:h-28"
                onClick={() => inputRef.current?.click()}
              >
                <ImagePlus className="size-6 sm:size-7" />
                <span className="text-sm font-medium sm:text-base">{t("scan.upload")}</span>
                <span className="text-center text-[11px] text-muted-foreground sm:text-xs">{t("scan.uploadHint")}</span>
              </Button>
            </div>
            <input
              ref={inputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => {
                onFile(e.target.files?.[0] ?? null);
                e.target.value = "";
              }}
            />
            {cameraError && (
              <div className="rounded-xl border border-dashed border-aji/40 bg-aji-soft/40 p-4 text-center text-sm text-destructive">
                {cameraError}
              </div>
            )}
          </div>
        )}

        {cameraActive && (
          <div className="mt-6 space-y-4 sm:mt-8">
            <div className="relative w-full overflow-hidden rounded-2xl bg-black">
              <video
                ref={videoRef}
                className="mx-auto max-h-[50vh] w-full object-cover sm:max-h-[60vh]"
                autoPlay
                playsInline
                muted
              />
              <div className="absolute inset-0 flex flex-col items-center justify-between p-3 sm:p-4">
                <p className="rounded-full bg-black/50 px-3 py-1 text-center text-xs text-white/90 sm:text-sm">
                  {t("scan.cameraHint")}
                </p>
                <div className="flex w-full items-center justify-center gap-2 sm:gap-3">
                  <Button
                    variant="outline"
                    size="lg"
                    className="rounded-full border-white/20 bg-white/10 text-white hover:bg-white/20"
                    onClick={stopCamera}
                  >
                    <X className="size-4" />
                    <span className="hidden sm:inline">{t("scan.cancel")}</span>
                  </Button>
                  <Button size="lg" className="rounded-full" onClick={takePhoto}>
                    <Camera className="mr-2 size-4" /> {t("scan.capture")}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {showTypeSelector && (
          <div className="mt-6 space-y-5 sm:mt-8 sm:space-y-6">
            <div className="relative w-full overflow-hidden rounded-2xl bg-muted">
              <img
                src={preview!}
                alt={t("scan.previewAlt")}
                className="mx-auto max-h-[20rem] w-full object-contain sm:max-h-[26rem]"
              />
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  clearFile();
                }}
                className="absolute right-3 top-3 grid size-9 place-items-center rounded-full bg-marino-dark/80 text-white backdrop-blur transition-colors hover:bg-aji"
                aria-label={t("scan.removeImage")}
              >
                <Trash2 className="size-4" />
              </button>
            </div>
            <div className="min-w-0 rounded-2xl border border-border bg-card p-4 sm:p-6">
              <h2 className="mb-4 text-center font-display text-lg font-bold sm:text-xl">{t("scan.chooseType")}</h2>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <Button
                  variant={recipeType === "traditional" ? "default" : "outline"}
                  size="lg"
                  className="flex h-24 w-full flex-col items-center justify-center gap-2 rounded-xl text-left sm:h-28"
                  onClick={() => setRecipeType("traditional")}
                >
                  <div className="flex w-full items-center gap-2">
                    <span className="text-2xl sm:text-3xl">🇵🇦</span>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-semibold sm:text-base">{t("scan.typeTraditional")}</p>
                      <p className="text-[11px] text-muted-foreground sm:text-xs">{t("scan.typeTraditionalDesc")}</p>
                    </div>
                  </div>
                  <Utensils className="size-5 text-culantro" />
                </Button>
                <Button
                  variant={recipeType === "healthy" ? "default" : "outline"}
                  size="lg"
                  className="flex h-24 w-full flex-col items-center justify-center gap-2 rounded-xl text-left sm:h-28"
                  onClick={() => setRecipeType("healthy")}
                >
                  <div className="flex w-full items-center gap-2">
                    <span className="text-2xl sm:text-3xl">🥗</span>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-semibold sm:text-base">{t("scan.typeHealthy")}</p>
                      <p className="text-[11px] text-muted-foreground sm:text-xs">{t("scan.typeHealthyDesc")}</p>
                    </div>
                  </div>
                  <Leaf className="size-5 text-aji" />
                </Button>
              </div>
            </div>
            <Button size="lg" className="w-full rounded-full" onClick={detect} disabled={detecting}>
              {detecting ? (
                <>
                  <Loader2 className="mr-2 size-4 animate-spin" />
                  {t("scan.analyzing")}
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 size-4" />
                  {t("scan.analyze")}
                </>
              )}
            </Button>
          </div>
        )}

        {error && (
          <div className="mt-5 w-full rounded-2xl border border-dashed border-aji/40 bg-aji-soft/40 p-4 text-center sm:p-5">
            <p className="text-sm font-medium text-destructive">{error}</p>
            <div className="mt-3 flex flex-wrap items-center justify-center gap-2">
              {file && !results && (
                <Button variant="outline" className="rounded-full" onClick={detect} disabled={detecting}>
                  {t("scan.retryPhoto")}
                </Button>
              )}
              {results && (
                <Button variant="outline" className="rounded-full" onClick={() => changeRecipeType("healthy")}>
                  {t("scan.retryPhoto")}
                </Button>
              )}
              <Button variant="ghost" className="rounded-full" onClick={clearFile}>
                {t("scan.changePhoto")}
              </Button>
            </div>
          </div>
        )}

        {detecting && (
          <div className="mt-8 flex flex-col items-center gap-4">
            <div className="mx-auto grid size-20 animate-pulse place-items-center rounded-full bg-maize-soft text-5xl">🍲</div>
            <p className="font-display text-xl font-bold">{t("scan.analyzing")}</p>
            <p className="text-sm text-muted-foreground">{t("scan.geminiHint")}</p>
          </div>
        )}

        {showResults && results && (
          <div className="mt-6 w-full space-y-6 sm:mt-8">
            <div className="min-w-0 rounded-2xl border border-border bg-card p-4">
              <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
                <h2 className="font-display text-lg font-bold sm:text-xl">{t("scan.resultsTitle")}</h2>
                <Button variant="ghost" size="sm" onClick={clearFile}>
                  <ChevronLeft className="mr-1 size-4" /> {t("scan.changePhoto")}
                </Button>
              </div>
              {results.detectedIngredients.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {results.detectedIngredients.map((d) => {
                    const tone = confidenceTone(d.confidence, t);
                    return (
                      <Badge
                        key={`${d.name}-${d.confidence}`}
                        variant={tone.cls.includes("culantro") ? "success" : tone.cls.includes("maize") ? "secondary" : "outline"}
                        className="gap-1.5 px-3 py-1.5 text-sm"
                      >
                        <span className={`rounded-full px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide ${tone.cls}`}>
                          {tone.label}
                        </span>{" "}
                        {d.name}
                      </Badge>
                    );
                  })}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">{t("scan.failed")}</p>
              )}
            </div>

            <div className="flex gap-2">
              <Button
                variant={recipeType === "traditional" ? "default" : "outline"}
                className="flex min-w-0 flex-1 items-center justify-center gap-2 rounded-xl py-3"
                onClick={() => changeRecipeType("traditional")}
                disabled={results.recipeType === "traditional" || typeBusy}
              >
                {typeBusy && results.recipeType === "healthy" ? <Loader2 className="size-4 animate-spin" /> : <Utensils className="size-4 shrink-0" />}
                <span className="truncate">{t("scan.typeTraditional")}</span>
              </Button>
              <Button
                variant={recipeType === "healthy" ? "default" : "outline"}
                className="flex min-w-0 flex-1 items-center justify-center gap-2 rounded-xl py-3"
                onClick={() => changeRecipeType("healthy")}
                disabled={results.recipeType === "healthy" || typeBusy}
              >
                {typeBusy && results.recipeType === "traditional" ? <Loader2 className="size-4 animate-spin" /> : <Leaf className="size-4 shrink-0" />}
                <span className="truncate">{t("scan.typeHealthy")}</span>
              </Button>
            </div>

            {recipeType === "traditional" && (
              <div className="min-w-0 space-y-4">
                <h2 className="font-display text-xl font-bold sm:text-2xl">{t("scan.traditionalTitle")}</h2>
                <p className="text-sm text-muted-foreground">{t("scan.traditionalSub")}</p>

                {results.traditionalRecipes === undefined ? (
                  <div className="flex justify-center py-8">
                    <Loader2 className="size-8 animate-spin text-culantro" />
                  </div>
                ) : results.traditionalRecipes && results.traditionalRecipes.length > 0 ? (
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {results.traditionalRecipes.map((recipe) => (
                      <TraditionalRecipeCard key={recipe.id ?? recipe.name} recipe={recipe} t={t} />
                    ))}
                  </div>
                ) : (
                  <div className="rounded-2xl border border-border bg-card p-8 text-center">
                    <span className="mx-auto grid size-14 place-items-center rounded-full bg-maize-soft text-2xl">🍳</span>
                    <h3 className="mt-4 font-display text-xl font-bold">{t("results.emptyTitle")}</h3>
                    <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">{t("results.emptyText")}</p>
                    <Button asChild className="mt-5 rounded-full bg-culantro">
                      <Link to={`/generar?ingredientes=${results.detectedIngredients.map((d) => d.name).join(",")}`}>
                        <Sparkles className="mr-2 size-4" /> {t("results.emptyGenerate")}
                      </Link>
                    </Button>
                  </div>
                )}
              </div>
            )}

            {recipeType === "healthy" && (
              <div className="min-w-0 space-y-4">
                {typeBusy && !results.healthyRecipe ? (
                  <div className="flex justify-center py-8">
                    <Loader2 className="size-8 animate-spin text-aji" />
                  </div>
                ) : results.healthyRecipe ? (
                  <HealthyRecipeView recipe={results.healthyRecipe} t={t} />
                ) : (
                  <div className="rounded-2xl border border-dashed border-aji/40 bg-aji-soft/40 p-8 text-center">
                    <p className="font-display text-xl font-bold text-destructive">{t("scan.error")}</p>
                    <Button variant="outline" className="mt-4 rounded-full" onClick={() => changeRecipeType("healthy")}>
                      {t("scan.retryPhoto")}
                    </Button>
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

function rateLimitMessage(e: unknown, t: (k: string) => string): string | null {
  const err = e as { code?: string };
  return err?.code === "rate_limit_exceeded" ? t("scan.rateLimitError") : null;
}