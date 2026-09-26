# ReSazón Loop — Design System

> Fuente de verdad de la identidad visual. Si un componente contradice esto, se corrige el componente.
> Generado por fase de consultoría de diseño — v1.0

---

## 1. Propósito del producto

Aplicación web panameña que convierte lo que tienes en la cocina en recetas reales:
escanea tu despensa, busca platos tradicionales por ingredientes, o genera una receta
original con IA. El lema es **"Menos desperdicio. Más sazón."** — el desperdicio se reduce,
el sabor se multiplica.

## 2. Público objetivo

- Panameños (y público hispano/latinx) de 25-55 años que cocinan en casa.
- Personas con ingredientes sueltos en la nevera que no saben qué hacer con ellos.
- Curiosos por la gastronomía panameña, marcas Nestlé conocidas (MAGGI®, LA LECHERA®, IDEAL®, Klim®).
- Tono cercano, familiar, sin hipérbole corporativa: **mesa de familia panameña, no campaña publicitaria**.

## 3. Personalidad de marca (5 rasgos)

1. **Casera** — sabe a cocina de la abuela, no a laboratorio.
2. **Panameña** — los sabores, platos e ingredientes de verdad (sancocho, hojaldas, chicheme).
3. **Manos en la masa** — imperfecto, táctil, con textura y anotaciones a mano.
4. **Cálida** — colores de comida en la mesa, sombras de papel, nada frío ni flotante.
5. **Curiosa con la IA** — la IA es la ayudante de cocina, no el protagonista visual.

## 4. Dirección visual — declaración

> **"El recetario de la abuela con la mesa puesta."** Papel crema con grano, subrayados
> ondulados a mano, stickers de plato, verduras con nombre propio. La tecnología existe
> debajo, nunca en la superficie.

Regla anti-genérica: **nada de glassmorphism, gradientes fríos, SaaS hero tipo "startup",
cards con bordes grises planos, ni mockups centrados genéricos.** Si un diseño parece
una plantilla de SaaS, se replantea.

## 5. Sistema de color

Referencia: `frontend/src/index.css` (`@theme`). Palette en oklch.

| Token | Rol | Valor |
|---|---|---|
| `--color-background` | Fondo papel | `oklch(0.97 0.014 90)` |
| `--color-foreground` | Texto principal | `oklch(0.23 0.02 75)` |
| `--color-card` | Superficie tarjeta | `oklch(0.995 0.006 90)` |
| `--color-primary` / `culantro` | Verde profundo (acciones principales) | `oklch(0.41 0.105 162)` |
| `--color-culantro-dark` | Verde casi negro (texto sobre marcos, foco) | `oklch(0.31 0.08 162)` |
| `--color-aji` | Rojo chile (acentos de energía, alertas suaves) | `oklch(0.62 0.2 32)` |
| `--color-aji-soft` | Fondo rojo suave (estados de error cálidos) | `oklch(0.9 0.06 42)` |
| `--color-maize` | Ámbar maíz (CTAs brillantes, selección) | `oklch(0.83 0.14 80)` |
| `--color-maize-soft` | Fondo ámbar suave | `oklch(0.93 0.05 88)` |
| `--color-marino` / `marino-dark` | Verde marino (barras/footer oscuro) | `oklch(0.26…0.2 0.05…0.06 162)` |
| `--color-muted-foreground` | Texto secundario | `oklch(0.5 0.03 75)` |
| `--color-border` | Borde suave cálido | `oklch(0.87 0.024 87)` |
| `--color-ring` | Focus ring | `oklch(0.42 0.11 162)` (culantro) |
| `--color-destructive` | Rojo de error | `oklch(0.58 0.21 30)` |

**Reglas de uso:**
- Verde culantro = acción principal, profundidad. Maíz = CTA brillante sobre oscuro/verde, realces, selección.
- Ají = energía y errores (nunca como CTA primario full).
- Marino = contraste oscuro (footer, header CTA), no fondos de card.
- Fondo siempre papel cálido; los gradientes solo en glifos decorativos o blobs difuminados de marca,
  nunca sobre texto de lectura (limitable a superficies de apoyo).

## 6. Tipografía

- **UI / cuerpo:** Inter (`--font-sans`). Texto 14-18px, leading relaxado, `text-pretty` para párrafos.
- **Display / titulares:** Fraunces (`--font-display`), serif con personalidad, `letter-spacing: -0.02em`. Titulares `font-black` con palabras‑clave coloreadas en culantro.
- **Manuscrita / anotaciones:** Caveat (`--font-hand`) para notas de borde, stickers, lema, precios de bodega, anotaciones que haría la abuela. Nunca para párrafos de lectura.
- Jerarquía: titular display → cuerpo Inter → anotación manuscrita. El subrayado de acento usa `underline-squiggle`.

## 7. Espacio, radio y sombra

- `--radius-lg/xl/2xl` para cards (1–2rem): formas acogedoras de mesa.
- Botones `rounded-full` como patrón de marca en CTAs del hero; `rounded-md` para inline.
- Sombras: `shadow-soft` (estado reposo) y `shadow-lift` (elevación, cards/hovery) — siempre
  sombras cálidas de papel, tono `0.23 0.02 75`, nunca negras puras ni glow.
- Espaciado base 4px; secciones mayores con `py-10…20` y `px-5` de margen lateral.

## 8. Texturas y firma visual

| Elemento | Definición | Uso |
|---|---|---|
| `bg-noise` | Grano SVG fractal (opacidad 0.035) | Fondos oscuros (footer marino) y superficies de marca |
| `underline-squiggle` | Subrayado ondulado SVG ámbar | Palabra‑clave del titular, enlaces de marca |
| Stickers | Capsules `rounded-full` rotadas `-rotate-*`, mano, sombra `shadow-lift` | Anotaciones sobre el hero (¡qué rico 🤤, con un buen chicheme 👌) |
| Emojis de plato | Fondo large emoji con `recipePalette()` | Cards de receta y mood board (p. ej. 🍗🍚) |
| Blobs difuminados | `rounded-full bg-*-soft blur-3xl` | Fondos decorativos del hero/footer, tamaño grande, sutiles |
| `animate-float` | Flotación lenta 7s | Cards/mood board del hero |
| `animate-marquee` | Cinta continua 34s | (firma opcional de marca) |

## 9. Patrones de componentes

- **Buttons** (`ui/button.tsx`): variantes `default` (culantro), `maize` (sobre marino), `aji`, `outline`, `ghost`, `marino-dark`, `destructive`. Focus `ring-culantro ring-offset-background`, `active:scale-[0.98]`, `transition-all duration-200`.
- **Cards** (`shared/recipe-card.tsx`): fondo `card`, borde `border-border`, `rounded-2xl`, `shadow-lift` al hover, imagen = `coverStyle()` emoji sobre fondo de marca, badge tipo (Tradicional/AI), match % en badge maíz-aji según nivel.
- **Skeletons**: no deben ser rectángulos grises genéricos — heredar textura `bg-noise` y el ritmo visual de la card que reemplazan.
- **Chips/filtros** (`Landing`): pills `rounded-full`, activo = culantro oscuro con texto `primary-foreground`, inactivo = `border`.
- **Inputs/picker** (`shared/ingredient-picker.tsx`): chips removibles de ingredientes, focus en ring culantro, lista de sugerencias sobre `popover`.
- **Badges** (`ui/badge.tsx`): pills pequeñas semánticas (categoría, dificultad, verificación).

## 10. Movimiento

- `Reveal` (framer-motion): fade+slide `y=24`, `ease [0.22,1,0.36,1]`, `whileInView once`, margen −60px. Respeta `prefers-reduced-motion` (`useReducedMotion` → sin animación).
- `float` y `marquee` lentos y de marca. **Nunca** animaciones rápidas/flash.
- Estados loading con esqueleto + mensaje manuscrito rotatorio (generate).

## 11. Accesibilidad base

- Contraste mínimo AA en texto (papel vs culantro/foreground cumple por diseño oklch).
- Focus visible siempre: `focus-visible:ring-2 ring-ring ring-offset-2`.
- `aria-label` en iconos y switcher de idioma; `aria-pressed` en botones de toggle.
- `prefers-reduced-motion` desactiva animaciones y suaviza scroll.
- Navegación por teclado: botones reales, `asChild`/`Slot` donde hay `<Link>`.
- Motivo de error con color (`destructive`/`aji`) + texto de ayuda (`results.apiErrorHint`), además de intento (retry).

## 12. Anti-patrones (NO-GO)

- ❌ Glassmorphism / blur sobre contenido de lectura / sombras con glow blanco.
- ❌ Gradientes fríos (azules-cian-morado) o fondos oscuros azulados genéricos.
- ❌ Hero de startup: "Empowering your kitchen with AI" + screenshot + mockup flotante genérico.
- ❌ Cards de borde 1px gris/mac, sin textura, sin emoji de plato, sin badges de marca.
- ❌ Skeleton genérico sin personalidad; spinners grises solos.
- ❌ Tipografía sin jerarquía (todo Inter, todo en negrita, sin display/hand).
- ❌ Emojis sin contexto, iconos genéricos sin `aria-label`.
- ❌ Shadows negras, `blur` excesivo, animaciones rápidas.

## 13. Checklist QA visual (previo a merge)

- [ ] Responsive: 360 / 768 / 1024 / 1440 sin overflow horizontal, hero y catálogo acomodan.
- [ ] Hover/focus en botones, chips, cards, links de nav y picker.
- [ ] Estados loading (skeleton con identidad) y error (destructive + hint + retry).
- [ ] Contraste y foco visible (tab) en todas las páginas.
- [ ] Idioma: es/en/fr sin cortes ni overflow en textos.
- [ ] Consistencia de título/breadcrumb entre landing, generar, escanear, receta y 404.