import { Plus, X } from "lucide-react";
import { useRef, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { useI18n } from "@/lib/i18n";

export const POPULAR = [
  "arroz",
  "pollo",
  "cebolla",
  "ajo",
  "culantro",
  "harina",
  "ñame",
  "plátano maduro",
  "tomate",
  "pimentón",
  "salchichas",
  "pescado",
  "camarones",
  "maíz",
  "yuca",
  "papas",
  "huevos",
  "zanahoria",
  "guandú",
  "leche",
  "queso",
  "aceite",
];

interface Props {
  value: string[];
  onChange: (next: string[]) => void;
  suggestions?: string[];
  placeholder?: string;
  autoFocus?: boolean;
  className?: string;
  maxVisibleSuggestions?: number;
}

export function IngredientPicker({
  value,
  onChange,
  suggestions = POPULAR,
  placeholder,
  autoFocus = false,
  className,
  maxVisibleSuggestions = 8,
}: Props) {
  const [draft, setDraft] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const { t } = useI18n();
  const placeholderText = placeholder ?? t("picker.placeholder");

  const add = (raw: string) => {
    const clean = raw.trim().toLowerCase().replace(/[.,;]+$/, "");
    if (!clean) return;
    onChange(value.includes(clean) ? value : [...value, clean]);
  };

  const commitDraft = () => {
    const parts = draft.split(",").map((s) => s.trim()).filter(Boolean);
    if (parts.length === 0) return;
    let next = [...value];
    for (const p of parts) {
      if (!next.some((v) => v.toLowerCase() === p.toLowerCase())) next.push(p.toLowerCase());
    }
    onChange(next);
    setDraft("");
  };

  const remove = (name: string) => onChange(value.filter((v) => v !== name));

  const visibleSuggestions = suggestions
    .filter((s) => s.toLowerCase().startsWith(draft.trim().toLowerCase()))
    .slice(0, maxVisibleSuggestions);
  const focused = draft.trim().length > 0;

  return (
    <div className={className}>
      <div className="relative">
        <Input
          ref={inputRef}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              commitDraft();
            } else if (e.key === "Backspace" && draft === "" && value.length > 0) {
              remove(value[value.length - 1]);
            }
          }}
          placeholder={placeholderText}
          autoFocus={autoFocus}
          className="h-12 rounded-xl pr-12 pl-4 text-[15px]"
          aria-label={t("picker.addIngredient")}
        />
        <button
          onClick={commitDraft}
          aria-label={t("picker.add")}
          className="absolute right-1.5 top-1/2 grid size-9 -translate-y-1/2 place-items-center rounded-lg bg-culantro text-primary-foreground transition-all hover:bg-culantro-dark active:scale-95"
        >
          <Plus className="size-4" />
        </button>
      </div>

      {focused && visibleSuggestions.length > 0 && (
        <ul className="mt-2 flex flex-wrap gap-1.5">
          {visibleSuggestions.map((s) => (
            <li key={s}>
              <button
                type="button"
                onClick={() => {
                  add(s);
                  setDraft("");
                  inputRef.current?.focus();
                }}
                className="rounded-full border border-border bg-card px-3 py-1 text-xs font-medium text-secondary-foreground transition-colors hover:border-culantro/40 hover:bg-culantro/10 hover:text-culantro-dark"
              >
                {s}
              </button>
            </li>
          ))}
        </ul>
      )}

      {value.length > 0 && (
        <div className="mt-3 flex flex-wrap items-center gap-1.5">
          {value.map((ing) => (
            <Badge key={ing} variant="secondary" className="gap-1.5 py-1 pl-3 pr-1.5 text-[13px]">
              {ing}
              <button
                onClick={() => remove(ing)}
                aria-label={t("picker.removeOne", { name: ing })}
                className="grid size-4 place-items-center rounded-full bg-foreground/10 text-foreground/70 transition-colors hover:bg-aji hover:text-white"
              >
                <X className="size-3" />
              </button>
            </Badge>
          ))}
          <span className="text-xs text-muted-foreground">
            {t(value.length === 1 ? "picker.countOne" : "picker.countMany", { n: value.length })}
          </span>
        </div>
      )}
    </div>
  );
}