import { useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Reveal } from "@/components/shared/reveal";
import { apiErrorMessage, useI18n } from "@/lib/i18n";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import type { DetectedIngredient } from "@/lib/types";

function confidenceTone(c: number, t: (k: string) => string) {
  if (c >= 0.8) return { label: t("conf.high"), cls: "bg-culantro/15 text-culantro-dark" };
  if (c >= 0.5) return { label: t("conf.medium"), cls: "bg-maize-soft text-[oklch(0.45_0.1_75)]" };
  return { label: t("conf.low"), cls: "bg-muted text-muted-foreground" };
}

import {
  ArrowLeft,
  Camera,
  ImagePlus,
  Loader2,
  Search,
  Sparkles,
  Trash2,
  X,
} from "lucide-react";

export function ScanPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const [detecting, setDetecting] = useState(false);
  const [detected, setDetected] = useState<DetectedIngredient[] | null>(null);
  const [kept, setKept] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const { t } = useI18n();

  function onFile(next: File | null) {
    if (!next) return;
    if (!next.type.startsWith("image/")) {
      setError(t("scan.onlyImages"));
      return;
    }
    setError(null);
    setFile(next);
    setDetected(null);
    setKept(new Set());
    setPreview(URL.createObjectURL(next));
  }

  async function detect() {
    if (!file) return;
    setDetecting(true);
    setError(null);
    try {
      const res = await api.scan(file);
      setDetected(res.detected_ingredients);
      setKept(new Set(res.detected_ingredients.map((d) => d.name)));
    } catch (e) {
      setError(apiErrorMessage(e, t));
    } finally {
      setDetecting(false);
    }
  }

  function searchWithKept() {
    const names = [...kept];
    if (names.length === 0) return;
    navigate(`/?ingredientes=${encodeURIComponent(names.join(","))}`);
  }

  const toggle = (name: string) => {
    setKept((prev) => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
  };

  return (
    <div className="mx-auto max-w-3xl px-5 py-10">
      <Link
        to="/"
        className="mb-6 inline-flex items-center gap-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
      >
        <ArrowLeft className="size-4" />
        {t("back.volver")}
      </Link>

      <Reveal>
        <span className="inline-flex items-center gap-2 rounded-full bg-culantro/12 px-3.5 py-1.5 text-xs font-semibold text-culantro-dark">
          <Camera className="size-3.5" />
          {t("scan.badge")}
        </span>
        <h1 className="mt-4 font-display text-4xl font-black tracking-tight">
          {t("scan.title")}
        </h1>
        <p className="mt-2 max-w-lg text-pretty text-muted-foreground">
          {t("scan.sub")}
        </p>

        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            onFile(e.dataTransfer.files?.[0] ?? null);
          }}
          onClick={() => inputRef.current?.click()}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
          }}
          className={cn(
            "mt-7 cursor-pointer rounded-3xl border-2 border-dashed p-6 text-center transition-all",
            dragging
              ? "border-culantro bg-culantro/8"
              : "border-border bg-card hover:border-culantro/40 hover:bg-muted/40",
          )}
        >
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => onFile(e.target.files?.[0] ?? null)}
          />

          {preview ? (
            <div className="relative overflow-hidden rounded-2xl">
              <img src={preview} alt={t("scan.previewAlt")} className="mx-auto max-h-[26rem] w-full object-cover" />
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setFile(null);
                  setPreview(null);
                }}
                className="absolute right-3 top-3 grid size-9 place-items-center rounded-full bg-marino-dark/80 text-white backdrop-blur transition-colors hover:bg-aji"
                aria-label={t("scan.removeImage")}
              >
                <Trash2 className="size-4" />
              </button>
            </div>
          ) : (
            <div className="py-10">
              <span className="mx-auto grid size-14 place-items-center rounded-full bg-maize-soft text-2xl">
                <ImagePlus className="size-6 text-[oklch(0.5_0.1_75)]" />
              </span>
              <p className="mt-4 font-medium">
                {dragging ? t("scan.dropActive") : t("scan.drop")}
              </p>
              <p className="mt-1 text-sm text-muted-foreground">
                {t("scan.orClick")}
              </p>
            </div>
          )}
        </div>

        {error && (
          <div className="mt-5 rounded-2xl border border-dashed border-aji/40 bg-aji-soft/40 p-5 text-center">
            <p className="text-sm font-medium text-destructive">{error}</p>
            {file && (
              <Button variant="outline" className="mt-3 rounded-full" onClick={() => onFile(file)}>
                {t("scan.retryPhoto")}
              </Button>
            )}
          </div>
        )}

        {file && !detected && !error && (
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <Button size="lg" onClick={detect} disabled={detecting} className="rounded-full">
              {detecting ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <Sparkles className="size-4" />
              )}
              {detecting ? t("scan.detecting") : t("scan.detect")}
            </Button>
            <span className="text-sm text-muted-foreground">
              {t("scan.geminiHint")}
            </span>
          </div>
        )}

        {detected && (
          <div className="mt-8">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2 className="font-display text-2xl font-bold">{t("scan.resultsTitle")}</h2>
              <span className="text-sm text-muted-foreground">
                {t("scan.toggleHint")}
              </span>
            </div>

            <div className="mt-4 flex flex-wrap gap-2">
              {detected.map((d) => {
                const tone = confidenceTone(d.confidence, t);
                const active = kept.has(d.name);
                return (
                  <button
                    key={d.name}
                    onClick={() => toggle(d.name)}
                    className={cn(
                      "group inline-flex items-center gap-2 rounded-full border px-3.5 py-2 text-sm font-medium transition-all",
                      active
                        ? "border-culantro/40 bg-culantro/10 text-culantro-dark"
                        : "border-border bg-card text-muted-foreground opacity-70 line-through",
                    )}
                  >
                    <span className={cn("rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide", tone.cls)}>
                      {tone.label}
                    </span>
                    {d.name}
                    <X className="size-3.5 opacity-60 transition-opacity group-hover:opacity-100" />
                  </button>
                );
              })}
            </div>

            <div className="mt-6 flex flex-wrap items-center gap-3">
              <Button size="lg" onClick={searchWithKept} disabled={kept.size === 0} className="rounded-full">
                <Search className="size-4" />
                {t("scan.searchWith", { n: kept.size > 0 ? kept.size : "…", s: kept.size === 1 ? "" : "s" })}
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="rounded-full"
                onClick={() => {
                  if (detected.length === 0) return;
                  if (kept.size === detected.length) {
                    setKept(new Set());
                  } else {
                    setKept(new Set(detected.map((d) => d.name)));
                  }
                }}
              >
                {kept.size === detected.length ? t("scan.clearAll") : t("scan.selectAll")}
              </Button>
            </div>

            {kept.size > 0 && (
              <div className="mt-4">
                <Badge variant="secondary" className="gap-1.5 py-1 pl-3 pr-1.5">
                  {t("scan.pantryBadge", { n: kept.size })}
                  <button onClick={() => setKept(new Set())} aria-label={t("scan.clearAll")}>
                    <X className="size-3.5" />
                  </button>
                </Badge>
              </div>
            )}
          </div>
        )}
      </Reveal>
    </div>
  );
}