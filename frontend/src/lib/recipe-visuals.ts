import type { CSSProperties } from "react";

interface RecipePalette {
  from: string;
  to: string;
  emoji: string;
  dark: boolean;
}

const PALETTES: RecipePalette[] = [
  { from: "#134E38", to: "#2E7D55", emoji: "🍲", dark: true },
  { from: "#C7461F", to: "#E66A2C", emoji: "🌭", dark: true },
  { from: "#B07E12", to: "#E8A93B", emoji: "🫓", dark: true },
  { from: "#1F4E79", to: "#3E78AD", emoji: "🍤", dark: true },
  { from: "#5B2F46", to: "#8C4566", emoji: "🥘", dark: true },
  { from: "#5A6B32", to: "#87994E", emoji: "🍛", dark: false },
  { from: "#2E2A24", to: "#5C5348", emoji: "🍢", dark: true },
  { from: "#7A3E1E", to: "#B06A37", emoji: "🍠", dark: true },
];

interface KindHint {
  test: RegExp;
  emoji: string;
}

const KIND_HINTS: KindHint[] = [
  { test: /pollo|gallina/i, emoji: "🍗" },
  { test: /sancocho|sopa|caldo/i, emoji: "🍲" },
  { test: /hojalda|pan|tortilla/i, emoji: "🫓" },
  { test: /salchicha/i, emoji: "🌭" },
  { test: /pescado|camar|marisco/i, emoji: "🦐" },
  { test: /plátano|platano|maduro/i, emoji: "🍌" },
  { test: /ensalada|verduras|vegetal/i, emoji: "🥗" },
  { test: /arroz/i, emoji: "🍚" },
];

function hashCode(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) {
    h = (Math.imul(31, h) + s.charCodeAt(i)) | 0;
  }
  return Math.abs(h);
}

export function recipePalette(name: string): RecipePalette {
  const nameLC = name.toLowerCase();
  let emoji = "🍽️";
  for (const hint of KIND_HINTS) {
    if (hint.test.test(nameLC)) {
      emoji = hint.emoji;
      break;
    }
  }
  const base = PALETTES[hashCode(name) % PALETTES.length] ?? PALETTES[0];
  return { ...base, emoji };
}

export function coverStyle(name: string): CSSProperties {
  const p = recipePalette(name);
  return {
    background: `radial-gradient(120% 160% at 12% 8%, ${p.to} 0%, ${p.from} 55%, color-mix(in oklab, ${p.from}, #101010 22%) 100%)`,
  };
}