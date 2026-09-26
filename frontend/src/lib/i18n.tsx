import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

export type Lang = "es" | "en" | "fr";

export const LANGS: { code: Lang; label: string; flag: string }[] = [
  { code: "es", label: "Español", flag: "🇪🇸" },
  { code: "en", label: "English", flag: "🇬🇧" },
  { code: "fr", label: "Français", flag: "🇫🇷" },
];

const ES: Record<string, string> = {
  // ── Header ──
  "nav.descubrir": "Descubrir",
  "nav.generar": "Generar",
  "nav.escanear": "Escanear",
  "cta.crearReceta": "Crear receta",
  "aria.openMenu": "Abrir menú",
  "aria.closeMenu": "Cerrar menú",

  // ── Landing ──
  "hero.badge": "Recetario “Nuestro Sabor Panamá”",
  "hero.slogan1": "Menos desperdicio.",
  "hero.slogan2": "Más sazón.",
  "hero.title1": "Lo que tienes en la cocina,",
  "hero.titleAccent": "convertido en sabor panameño",
  "hero.sub":
    "Di qué ingredientes tienes y te decimos qué tradicional puedes preparar — o usa la IA para inventar algo nuevo. Sin recetas genéricas: solo cocina de verdad.",
  "search.button": "Buscar recetas",
  "search.loading": "Buscando…",
  "hero.scanAlt": "O escanea tu foto",
  "hero.sticker1": "¡qué rico! 🤤",
  "hero.sticker2": "con un buen chicheme 👌",
  "hero.note1": "el domingo es sagrado",
  "hero.note2": "la reina del desayuno",
  "hero.note3": "dulce y espesito",

  // ── Resultados ──
  "results.title": "Tus recetas",
  "results.loading": "Consultando el recetario…",
  "results.error": "No pudimos completar la búsqueda.",
  "results.countOne": "{n} receta encontrada con lo que tienes",
  "results.countMany": "{n} recetas encontradas con lo que tienes",
  "results.generateNew": "Crear algo nuevo con IA",
  "results.apiErrorHint": "Revisa que la API esté corriendo en el puerto 8000 y reintenta.",
  "results.emptyTitle": "Sin suerte con la despensa…",
  "results.emptyText":
    "No encontramos tradición panameña para esos ingredientes, pero la IA puede improvisar algo delicioso.",
  "results.emptyGenerate": "Generar con IA",

  // ── Cómo funciona ──
  "how.label": "Así de fácil",
  "how.subtitle": "De tu nevera a la mesa, en tres pasos",
  "how.step1Title": "Cuéntanos qué tienes",
  "how.step1Text":
    "Sube una foto de tu despensa o escribe tus ingredientes. La IA reconoce lo que ves.",
  "how.step2Title": "Elige tu receta",
  "how.step2Text":
    "Tradiciones panameñas rankeadas por cuánto cubren lo que tienes, con lo que falta claro.",
  "how.step3Title": "O crea algo nuevo",
  "how.step3Text":
    "¿Nada clásico calza? Generamos una receta con tus ingredientes y tus metas.",

  // ── Showcase ──
  "showcase.label": "El recetario",
  "showcase.title": "Clásicos que ya puedes cocinar",
  "showcase.text":
    "Tradiciones de “Nuestro Sabor Panamá”, listas para explorar plato por plato.",

  // ── CTA final ──
  "final.title": "¿Tu despensa no alcanza para nada tradicional?",
  "final.text":
    "Generamos una receta 100% con lo que tienes, con nutrición estimada y pasos claros.",
  "final.generate": "Generar receta con IA",
  "final.scan": "Escanear mi despensa",

  // ── Filtros catálogo ──
  "filters.title": "Filtrar",
  "filters.category": "Categoría",
  "filters.difficulty": "Dificultad",
  "filters.categoryAll": "Todas",
  "filters.difficultyAll": "Cualquiera",
  "filters.clear": "Limpiar filtros",

  // ── Dificultad ──
  "difficulty.facil": "Fácil",
  "difficulty.media": "Media",
  "difficulty.dificil": "Difícil",

  // ── Recipe card ──
  "card.ai": "Con IA",
  "card.healthy": "Saludable",
  "card.traditional": "Tradicional",
  "card.simple": "Sencilla",
  "card.postre": "Postre",
  "card.view": "Ver receta",
  "card.min": "{n} min",
  "card.persons": "{n} pers.",
  "card.available": "{n} disponibles",
  "card.missing": "Te faltaría: {list}",
  "card.andMore": "y {n} más",
  "card.plusMore": "+{n}",
  "card.verified": "Panamá verificado",
  "card.source": "Recetas Nestlé CAM",

  // ── RecipeView ──
  "view.ingredients": "Ingredientes",
  "view.preparation": "Preparación",
  "view.items": "{n} ítems",
  "view.optional": "opcional",
  "view.brand": "Marca destacada",
  "view.perServing": "Por porción",
  "view.persons": "{n} personas",
  "view.generated": "Generada con IA",
  "view.adapted": "Adaptación saludable",
  "view.traditional": "Tradicional",
  "view.category": "Categoría",
  "view.sourceLink": "Ver fuente original",
  "view.nutProtein": "Proteína",
  "view.nutCarbs": "Carbohidratos",
  "view.nutFat": "Grasas",
  "view.nutFiber": "Fibra",

  // ── Generate ──
  "back.volver": "Volver",
  "gen.badge": "Creación con IA",
  "gen.title": "Genera una receta con lo que tienes",
  "gen.sub":
    "La IA toma tus ingredientes, piensa como un cocinero panameño y te devuelve una receta con cantidades, pasos y nutrición estimada.",
  "gen.goalLabel": "Meta de cocina (opcional)",
  "goal.none": "Sin meta específica",
  "goal.masProteinas": "Más proteína",
  "goal.menosSodio": "Menos sodio",
  "goal.bajoGrasas": "Bajo en grasas",
  "goal.altoFibra": "Más fibra",
  "goal.vegetariano": "Vegetariano",
  "goal.sinGluten": "Sin gluten",
  "gen.button": "Cocinar con IA",
  "gen.loading": "Generando…",
  "gen.surprise": "Sorpresa",
  "gen.loading1": "Rumiando la despensa…",
  "gen.loading2": "Consultando a la abuela (IA)…",
  "gen.loading3": "Midiendo a ojo de buen cubero…",
  "gen.loading4": "Ajustando el sazón…",
  "gen.loading5": "Poniendo la olla al fuego…",
  "gen.loading6": "Cruzando los dedos para que no se pegue…",
  "gen.loadingHint": "Con {n} ingrediente{s} · suele tardar unos segundos",
  "gen.errorDisabled": "IA desactivada",
  "gen.errorBusy": "Gemini está saturado justo ahora",
  "gen.retry": "Reintentar",
  "gen.readyBadge": "Generada para ti",
  "gen.failed": "No se pudo generar la receta",

  // ── Scan ──
  "scan.badge": "Foto de la despensa",
  "scan.title": "Escanea lo que tienes",
  "scan.sub":
    "Sácale una foto a tu despensa o a la mesa después de mercado y la IA reconoce los ingredientes que tienes a la mano.",
  "scan.drop": "Arrastra tu foto aquí",
  "scan.dropActive": "¡Suéltala aquí!",
  "scan.orClick": "o haz clic para elegir un archivo · JPG, PNG o WebP",
  "scan.previewAlt": "Vista previa de tu foto",
  "scan.removeImage": "Quitar imagen",
  "scan.onlyImages": "Solo aceptamos imágenes (JPG, PNG, WebP…).",
  "scan.detect": "Detectar ingredientes",
  "scan.detecting": "Reconociendo…",
  "scan.geminiHint": "Gemini revisa tu foto en unos segundos",
  "scan.failed": "No pudimos detectar los ingredientes",
  "scan.retryPhoto": "Reintentar con esta foto",
  "scan.resultsTitle": "Ingredientes detectados",
  "scan.toggleHint": "Toca para quitar los que no quieras usar",
  "scan.searchWith": "Buscar recetas con {n} ingrediente{s}",
  "scan.selectAll": "Marcar todos",
  "scan.clearAll": "Quitar todos",
  "scan.pantryBadge": "{n} en tu despensa virtual",
  "conf.high": "alta",
  "conf.medium": "media",
  "conf.low": "baja",

  // ── Recipe page ──
  "recipe.back": "Volver a descubrir",
  "recipe.notFound": "Ups… no encontramos esa receta.",
  "recipe.backHome": "Volver al inicio",
  "recipe.healthyTitle": "¿Quieres una versión más saludable?",
  "recipe.healthyText":
    "Adaptamos {name} con menos grasa, menos sodio y más fibra — sin perder el sabor.",
  "recipe.healthyBtn": "Hacer versión saludable",
  "recipe.reinventing": "Reinventando…",
  "recipe.adaptedBadge": "Adaptación saludable",
  "recipe.adaptedHint": "Generada con IA a partir de {name}",
  "recipe.liked": "¿Te gustó?",
  "recipe.exploreMore": "Explorar más recetas",

  // ── Not found ──
  "notfound.title": "Se nos quemó la página",
  "notfound.text": "El 404 que encontraste no estaba en el recetario. Volvamos a la cocina.",
  "notfound.home": "Ir al inicio",

  // ── Footer ──
  "footer.tagline":
    "Recetas panameñas hechas con lo que tienes en la cocina. De la mesa de las abuelas al poder de la IA.",
  "footer.explore": "Explora",
  "footer.about": "Acerca de",
  "footer.discover": "Descubrir recetas",
  "footer.generate": "Generar con IA",
  "footer.scan": "Escanear ingredientes",
  "footer.made": "Hecho en Panamá 🇵🇦",
  "footer.recetario": "Recetario “Nuestro Sabor Panamá”",
  "footer.disclaimer":
    "© {year} ReSazón Loop. Los valores nutricionales son estimados y no constituyen consejo médico.",
  "footer.enjoy": "¡Buen provecho!",

  // ── Ingredient picker ──
  "picker.placeholder": "Escribe un ingrediente y presiona Enter…",
  "picker.add": "Añadir",
  "picker.addIngredient": "Añadir ingrediente",
  "picker.countOne": "{n} ingrediente",
  "picker.countMany": "{n} ingredientes",
  "picker.removeOne": "Quitar {name}",

  // ── Errores de API ──
  "aria.home": "ReSazón Loop — inicio",
  "err.notFound": "No pudimos encontrar ese recurso.",
  "err.validation": "Los datos enviados no son válidos.",
  "err.image": "La imagen no es válida.",
  "err.upstream": "El proveedor de IA no pudo procesar la solicitud.",
  "err.gemini": "La IA devolvió una respuesta no procesable.",
  "err.rag": "Hubo un error al consultar el recetario.",
  "err.aiDisabled": "La IA está desactivada: define GEMINI_AI_ENABLED=true en backend/.env.",
  "err.internal": "Ocurrió un error inesperado.",
};

const EN: Record<string, string> = {
  "nav.descubrir": "Discover",
  "nav.generar": "Generate",
  "nav.escanear": "Scan",
  "cta.crearReceta": "Create recipe",
  "aria.openMenu": "Open menu",
  "aria.closeMenu": "Close menu",

  "hero.badge": "“Nuestro Sabor Panamá” recipe box",
  "hero.slogan1": "Less waste.",
  "hero.slogan2": "More flavor.",
  "hero.title1": "Whatever you have in your kitchen,",
  "hero.titleAccent": "turned into Panamanian flavor",
  "hero.sub":
    "Tell us what ingredients you have and we'll tell you what traditional dish you can make — or use AI to invent something new. No generic recipes: real cooking only.",
  "search.button": "Search recipes",
  "search.loading": "Searching…",
  "hero.scanAlt": "Or scan your photo",
  "hero.sticker1": "so tasty! 🤤",
  "hero.sticker2": "with a good chicheme 👌",
  "hero.note1": "Sunday is sacred",
  "hero.note2": "queen of breakfast",
  "hero.note3": "sweet and thick",

  "results.title": "Your recipes",
  "results.loading": "Checking the recipe box…",
  "results.error": "We couldn't complete the search.",
  "results.countOne": "{n} recipe found with what you have",
  "results.countMany": "{n} recipes found with what you have",
  "results.generateNew": "Create something new with AI",
  "results.apiErrorHint": "Check that the API is running on port 8000 and try again.",
  "results.emptyTitle": "No luck with the pantry…",
  "results.emptyText":
    "We didn't find Panamanian tradition for those ingredients, but AI can improvise something delicious.",
  "results.emptyGenerate": "Generate with AI",

  "how.label": "That easy",
  "how.subtitle": "From your fridge to the table, in three steps",
  "how.step1Title": "Tell us what you have",
  "how.step1Text":
    "Upload a photo of your pantry or type your ingredients. AI recognizes what you see.",
  "how.step2Title": "Pick your recipe",
  "how.step2Text":
    "Panamanian traditions ranked by how well they cover what you have, with what's missing spelled out.",
  "how.step3Title": "Or create something new",
  "how.step3Text":
    "No classic fits? We generate a recipe from your ingredients and your goals.",

  "showcase.label": "The recipe box",
  "showcase.title": "Classics you can cook today",
  "showcase.text":
    "Traditions from “Nuestro Sabor Panamá”, ready to explore dish by dish.",

  "final.title": "Is your pantry not enough for anything traditional?",
  "final.text":
    "We generate a recipe 100% from what you have, with estimated nutrition and clear steps.",
  "final.generate": "Generate recipe with AI",
  "final.scan": "Scan my pantry",

  "filters.title": "Filter",
  "filters.category": "Category",
  "filters.difficulty": "Difficulty",
  "filters.categoryAll": "All",
  "filters.difficultyAll": "Any",
  "filters.clear": "Clear filters",

  "difficulty.facil": "Easy",
  "difficulty.media": "Medium",
  "difficulty.dificil": "Hard",

  "card.ai": "AI",
  "card.healthy": "Healthy",
  "card.traditional": "Traditional",
  "card.simple": "Simple",
  "card.postre": "Dessert",
  "card.view": "View recipe",
  "card.min": "{n} min",
  "card.persons": "{n} pers.",
  "card.available": "{n} available",
  "card.missing": "You'd be missing: {list}",
  "card.andMore": "and {n} more",
  "card.plusMore": "+{n}",
  "card.verified": "Verified Panamá",
  "card.source": "Nestlé CAM recipes",

  "view.ingredients": "Ingredients",
  "view.preparation": "Preparation",
  "view.items": "{n} items",
  "view.optional": "optional",
  "view.brand": "Featured brand",
  "view.perServing": "Per serving",
  "view.persons": "{n} people",
  "view.generated": "AI generated",
  "view.adapted": "Healthy adaptation",
  "view.traditional": "Traditional",
  "view.category": "Category",
  "view.sourceLink": "View original source",
  "view.nutProtein": "Protein",
  "view.nutCarbs": "Carbs",
  "view.nutFat": "Fat",
  "view.nutFiber": "Fiber",

  "back.volver": "Back",
  "gen.badge": "AI creation",
  "gen.title": "Generate a recipe from what you have",
  "gen.sub":
    "AI takes your ingredients, thinks like a Panamanian cook and returns a recipe with quantities, steps and estimated nutrition.",
  "gen.goalLabel": "Cooking goal (optional)",
  "goal.none": "No specific goal",
  "goal.masProteinas": "More protein",
  "goal.menosSodio": "Less sodium",
  "goal.bajoGrasas": "Low fat",
  "goal.altoFibra": "More fiber",
  "goal.vegetariano": "Vegetarian",
  "goal.sinGluten": "Gluten-free",
  "gen.button": "Cook with AI",
  "gen.loading": "Generating…",
  "gen.surprise": "Surprise me",
  "gen.loading1": "Rummaging through the pantry…",
  "gen.loading2": "Asking grandma (AI)…",
  "gen.loading3": "Measuring by eye…",
  "gen.loading4": "Adjusting the seasoning…",
  "gen.loading5": "Putting the pot on…",
  "gen.loading6": "Crossing our fingers it won't stick…",
  "gen.loadingHint": "With {n} ingredient{s} · usually takes a few seconds",
  "gen.errorDisabled": "AI disabled",
  "gen.errorBusy": "Gemini is overloaded right now",
  "gen.retry": "Retry",
  "gen.readyBadge": "Made for you",
  "gen.failed": "Couldn't generate the recipe",

  "scan.badge": "Pantry photo",
  "scan.title": "Scan what you have",
  "scan.sub":
    "Snap a photo of your pantry or the table right after market day and AI picks out the ingredients you have on hand.",
  "scan.drop": "Drop your photo here",
  "scan.dropActive": "Drop it here!",
  "scan.orClick": "or click to choose a file · JPG, PNG or WebP",
  "scan.previewAlt": "Preview of your photo",
  "scan.removeImage": "Remove image",
  "scan.onlyImages": "We only accept images (JPG, PNG, WebP…).",
  "scan.detect": "Detect ingredients",
  "scan.detecting": "Recognizing…",
  "scan.geminiHint": "Gemini reviews your photo in a few seconds",
  "scan.failed": "We couldn't detect the ingredients",
  "scan.retryPhoto": "Retry with this photo",
  "scan.resultsTitle": "Detected ingredients",
  "scan.toggleHint": "Tap to remove the ones you don't want to use",
  "scan.searchWith": "Search recipes with {n} ingredient{s}",
  "scan.selectAll": "Select all",
  "scan.clearAll": "Clear all",
  "scan.pantryBadge": "{n} in your virtual pantry",
  "conf.high": "high",
  "conf.medium": "medium",
  "conf.low": "low",

  "recipe.back": "Back to discover",
  "recipe.notFound": "Oops… we couldn't find that recipe.",
  "recipe.backHome": "Back to home",
  "recipe.healthyTitle": "Want a healthier version?",
  "recipe.healthyText":
    "We adapt {name} with less fat, less sodium and more fiber — without losing the flavor.",
  "recipe.healthyBtn": "Make a healthy version",
  "recipe.reinventing": "Reinventing…",
  "recipe.adaptedBadge": "Healthy adaptation",
  "recipe.adaptedHint": "AI generated from {name}",
  "recipe.liked": "Liked it?",
  "recipe.exploreMore": "Explore more recipes",

  "notfound.title": "We burned the page",
  "notfound.text": "The 404 you found wasn't in the recipe box. Let's go back to the kitchen.",
  "notfound.home": "Go home",

  "footer.tagline":
    "Panamanian recipes made with what you have in your kitchen. From grandma's table to the power of AI.",
  "footer.explore": "Explore",
  "footer.about": "About",
  "footer.discover": "Discover recipes",
  "footer.generate": "Generate with AI",
  "footer.scan": "Scan ingredients",
  "footer.made": "Made in Panama 🇵🇦",
  "footer.recetario": "“Nuestro Sabor Panamá” recipe box",
  "footer.disclaimer":
    "© {year} ReSazón Loop. Nutritional values are estimates and do not constitute medical advice.",
  "footer.enjoy": "Enjoy your meal!",

  "picker.placeholder": "Type an ingredient and press Enter…",
  "picker.add": "Add",
  "picker.addIngredient": "Add ingredient",
  "picker.countOne": "{n} ingredient",
  "picker.countMany": "{n} ingredients",
  "picker.removeOne": "Remove {name}",

  // ── API errors ──
  "aria.home": "ReSazón Loop — home",
  "err.notFound": "We couldn't find that resource.",
  "err.validation": "The data you sent isn't valid.",
  "err.image": "That image isn't valid.",
  "err.upstream": "The AI provider couldn't process the request.",
  "err.gemini": "The AI returned an unusable response.",
  "err.rag": "Something went wrong querying the recipe book.",
  "err.aiDisabled": "AI is disabled: set GEMINI_AI_ENABLED=true in backend/.env.",
  "err.internal": "An unexpected error occurred.",
};

const FR: Record<string, string> = {
  "nav.descubrir": "Découvrir",
  "nav.generar": "Générer",
  "nav.escanear": "Scanner",
  "cta.crearReceta": "Créer une recette",
  "aria.openMenu": "Ouvrir le menu",
  "aria.closeMenu": "Fermer le menu",

  "hero.badge": "Recueil « Nuestro Sabor Panamá »",
  "hero.slogan1": "Moins de gaspillage.",
  "hero.slogan2": "Plus de saveur.",
  "hero.title1": "Ce que vous avez dans la cuisine,",
  "hero.titleAccent": "transformé en saveur panaméenne",
  "hero.sub":
    "Dites-nous quels ingrédients vous avez et nous vous disons quel plat traditionnel préparer — ou utilisez l'IA pour inventer quelque chose de nouveau. Pas de recettes génériques : de la vraie cuisine.",
  "search.button": "Rechercher des recettes",
  "search.loading": "Recherche…",
  "hero.scanAlt": "Ou scannez votre photo",
  "hero.sticker1": "délicieux ! 🤤",
  "hero.sticker2": "avec un bon chicheme 👌",
  "hero.note1": "le dimanche c'est sacré",
  "hero.note2": "la reine du petit-déj",
  "hero.note3": "doux et épais",

  "results.title": "Vos recettes",
  "results.loading": "Consultation du recueil…",
  "results.error": "Nous n'avons pas pu terminer la recherche.",
  "results.countOne": "{n} recette trouvée avec ce que vous avez",
  "results.countMany": "{n} recettes trouvées avec ce que vous avez",
  "results.generateNew": "Créer quelque chose de nouveau avec l'IA",
  "results.apiErrorHint": "Vérifiez que l'API tourne sur le port 8000 et réessayez.",
  "results.emptyTitle": "Pas de chance avec le garde-manger…",
  "results.emptyText":
    "Nous n'avons pas trouvé de tradition panaméenne pour ces ingrédients, mais l'IA peut improviser quelque chose de délicieux.",
  "results.emptyGenerate": "Générer avec l'IA",

  "how.label": "C'est si simple",
  "how.subtitle": "Du frigo à la table, en trois étapes",
  "how.step1Title": "Dites-nous ce que vous avez",
  "how.step1Text":
    "Téléversez une photo de votre garde-manger ou saisissez vos ingrédients. L'IA reconnaît ce que vous voyez.",
  "how.step2Title": "Choisissez votre recette",
  "how.step2Text":
    "Des traditions panaméennes classées selon ce que vous avez, avec ce qui manque bien indiqué.",
  "how.step3Title": "Ou créez quelque chose de nouveau",
  "how.step3Text":
    "Rien de classique ne colle ? Nous générons une recette avec vos ingrédients et vos objectifs.",

  "showcase.label": "Le recueil",
  "showcase.title": "Des classiques à cuisiner aujourd'hui",
  "showcase.text":
    "Les traditions de « Nuestro Sabor Panamá », prêtes à explorer plat par plat.",

  "final.title": "Votre garde-manger ne suffit pour rien de traditionnel ?",
  "final.text":
    "Nous générons une recette 100 % avec ce que vous avez, avec une nutrition estimée et des étapes claires.",
  "final.generate": "Générer une recette avec l'IA",
  "final.scan": "Scanner mon garde-manger",

  "filters.title": "Filtrer",
  "filters.category": "Catégorie",
  "filters.difficulty": "Difficulté",
  "filters.categoryAll": "Toutes",
  "filters.difficultyAll": "Peu importe",
  "filters.clear": "Effacer les filtres",

  "difficulty.facil": "Facile",
  "difficulty.media": "Moyenne",
  "difficulty.dificil": "Difficile",

  "card.ai": "IA",
  "card.healthy": "Sain",
  "card.traditional": "Traditionnel",
  "card.simple": "Simple",
  "card.postre": "Dessert",
  "card.view": "Voir la recette",
  "card.min": "{n} min",
  "card.persons": "{n} pers.",
  "card.available": "{n} disponibles",
  "card.missing": "Il vous manquerait : {list}",
  "card.andMore": "et {n} de plus",
  "card.plusMore": "+{n}",
  "card.verified": "Panamá vérifié",
  "card.source": "Recettes Nestlé CAM",

  "view.ingredients": "Ingrédients",
  "view.preparation": "Préparation",
  "view.items": "{n} éléments",
  "view.optional": "optionnel",
  "view.brand": "Marque mise en avant",
  "view.perServing": "Par portion",
  "view.persons": "{n} personnes",
  "view.generated": "Générée par l'IA",
  "view.adapted": "Adaptation saine",
  "view.traditional": "Traditionnel",
  "view.category": "Catégorie",
  "view.sourceLink": "Voir la source originale",
  "view.nutProtein": "Protéines",
  "view.nutCarbs": "Glucides",
  "view.nutFat": "Lipides",
  "view.nutFiber": "Fibres",

  "back.volver": "Retour",
  "gen.badge": "Création avec l'IA",
  "gen.title": "Générez une recette avec ce que vous avez",
  "gen.sub":
    "L'IA prend vos ingrédients, pense comme un cuisinier panaméen et vous rend une recette avec quantités, étapes et nutrition estimée.",
  "gen.goalLabel": "Objectif culinaire (facultatif)",
  "goal.none": "Aucun objectif précis",
  "goal.masProteinas": "Plus de protéines",
  "goal.menosSodio": "Moins de sodium",
  "goal.bajoGrasas": "Peu de gras",
  "goal.altoFibra": "Plus de fibres",
  "goal.vegetariano": "Végétarien",
  "goal.sinGluten": "Sans gluten",
  "gen.button": "Cuisiner avec l'IA",
  "gen.loading": "Génération…",
  "gen.surprise": "Surprise",
  "gen.loading1": "On fouille le garde-manger…",
  "gen.loading2": "On consulte grand-mère (IA)…",
  "gen.loading3": "On mesure à l'œil…",
  "gen.loading4": "On ajuste l'assaisonnement…",
  "gen.loading5": "On met la casserole sur le feu…",
  "gen.loading6": "On croise les doigts pour que ça n'attache pas…",
  "gen.loadingHint": "Avec {n} ingrédient{s} · prend généralement quelques secondes",
  "gen.errorDisabled": "IA désactivée",
  "gen.errorBusy": "Gemini est saturé en ce moment",
  "gen.retry": "Réessayer",
  "gen.readyBadge": "Fait pour vous",
  "gen.failed": "Impossible de générer la recette",

  "scan.badge": "Photo du garde-manger",
  "scan.title": "Scannez ce que vous avez",
  "scan.sub":
    "Photographiez votre garde-manger ou la table après le marché et l'IA reconnaît les ingrédients que vous avez sous la main.",
  "scan.drop": "Déposez votre photo ici",
  "scan.dropActive": "Déposez-la ici !",
  "scan.orClick": "ou cliquez pour choisir un fichier · JPG, PNG ou WebP",
  "scan.previewAlt": "Aperçu de votre photo",
  "scan.removeImage": "Retirer l'image",
  "scan.onlyImages": "Nous n'acceptons que des images (JPG, PNG, WebP…).",
  "scan.detect": "Détecter les ingrédients",
  "scan.detecting": "Reconnaissance…",
  "scan.geminiHint": "Gemini examine votre photo en quelques secondes",
  "scan.failed": "Impossible de détecter les ingrédients",
  "scan.retryPhoto": "Réessayer avec cette photo",
  "scan.resultsTitle": "Ingrédients détectés",
  "scan.toggleHint": "Touchez pour retirer ceux que vous ne voulez pas utiliser",
  "scan.searchWith": "Chercher des recettes avec {n} ingrédient{s}",
  "scan.selectAll": "Tout sélectionner",
  "scan.clearAll": "Tout retirer",
  "scan.pantryBadge": "{n} dans votre garde-manger virtuel",
  "conf.high": "haute",
  "conf.medium": "moyenne",
  "conf.low": "basse",

  "recipe.back": "Retour à la découverte",
  "recipe.notFound": "Oups… impossible de trouver cette recette.",
  "recipe.backHome": "Retour à l'accueil",
  "recipe.healthyTitle": "Envie d'une version plus saine ?",
  "recipe.healthyText":
    "Nous adaptons {name} avec moins de gras, moins de sodium et plus de fibres — sans perdre la saveur.",
  "recipe.healthyBtn": "Faire une version saine",
  "recipe.reinventing": "Réinvention…",
  "recipe.adaptedBadge": "Adaptation saine",
  "recipe.adaptedHint": "Générée par l'IA à partir de {name}",
  "recipe.liked": "Ça vous a plu ?",
  "recipe.exploreMore": "Explorer plus de recettes",

  "notfound.title": "On a brûlé la page",
  "notfound.text": "Le 404 que vous avez trouvé n'était pas dans le recueil. Retournons en cuisine.",
  "notfound.home": "Aller à l'accueil",

  "footer.tagline":
    "Des recettes panaméennes faites avec ce que vous avez dans la cuisine. De la table des grand-mères au pouvoir de l'IA.",
  "footer.explore": "Explorer",
  "footer.about": "À propos",
  "footer.discover": "Découvrir des recettes",
  "footer.generate": "Générer avec l'IA",
  "footer.scan": "Scanner les ingrédients",
  "footer.made": "Fait au Panama 🇵🇦",
  "footer.recetario": "Recueil « Nuestro Sabor Panamá »",
  "footer.disclaimer":
    "© {year} ReSazón Loop. Les valeurs nutritionnelles sont des estimations et ne constituent pas un avis médical.",
  "footer.enjoy": "Bon appétit !",

  "picker.placeholder": "Saisissez un ingrédient puis Entrée…",
  "picker.add": "Ajouter",
  "picker.addIngredient": "Ajouter un ingrédient",
  "picker.countOne": "{n} ingrédient",
  "picker.countMany": "{n} ingrédients",
  "picker.removeOne": "Retirer {name}",

  // ── Erreurs d'API ──
  "aria.home": "ReSazón Loop — accueil",
  "err.notFound": "Nous n'avons pas pu trouver cette ressource.",
  "err.validation": "Les données envoyées ne sont pas valides.",
  "err.image": "Cette image n'est pas valide.",
  "err.upstream": "Le fournisseur d'IA n'a pas pu traiter la demande.",
  "err.gemini": "L'IA a renvoyé une réponse inutilisable.",
  "err.rag": "Une erreur est survenue en interrogeant le recueil.",
  "err.aiDisabled": "L'IA est désactivée : définissez GEMINI_AI_ENABLED=true dans backend/.env.",
  "err.internal": "Une erreur inattendue est survenue.",
};

const DICTS: Record<Lang, Record<string, string>> = { es: ES, en: EN, fr: FR };

const STORAGE_KEY = "rezazon.lang";

function readStoredLang(): Lang {
  const stored = typeof window !== "undefined" ? localStorage.getItem(STORAGE_KEY) : null;
  return stored === "es" || stored === "en" || stored === "fr" ? stored : "es";
}

interface I18nValue {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: (key: string, vars?: Record<string, string | number>) => string;
}

const I18nContext = createContext<I18nValue | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(readStoredLang);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, lang);
    document.documentElement.lang = lang;
  }, [lang]);

  const setLang = useCallback((next: Lang) => setLangState(next), []);

  const t = useCallback(
    (key: string, vars?: Record<string, string | number>) => {
      let value = DICTS[lang][key] ?? DICTS.es[key] ?? key;
      if (vars) {
        for (const [name, raw] of Object.entries(vars)) {
          value = value.replaceAll(`{${name}}`, String(raw));
        }
      }
      return value;
    },
    [lang],
  );

  const value = useMemo(() => ({ lang, setLang, t }), [lang, setLang, t]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nValue {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n debe usarse dentro de <I18nProvider>");
  return ctx;
}

function normalizeAccents(value: string): string {
  return value.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

export function difficultySlug(raw: string | null | undefined): "facil" | "media" | "dificil" | null {
  const value = normalizeAccents(raw?.toLowerCase() ?? "");
  if (!value) return null;
  if (value.includes("facil")) return "facil";
  if (value.includes("dificil") || value.includes("alta")) return "dificil";
  return "media";
}

export function difficultyKey(slug: string | null | undefined): string {
  if (!slug) return "difficulty.media";
  return `difficulty.${slug}`;
}

export function plural(n: number): string {
  return n === 1 ? "" : "s";
}

const ERROR_KEYS: Record<string, string> = {
  not_found: "err.notFound",
  validation_error: "err.validation",
  image_validation_error: "err.image",
  upstream_ai_error: "err.upstream",
  ai_response_error: "err.gemini",
  rag_error: "err.rag",
  ai_not_configured: "err.aiDisabled",
  internal_error: "err.internal",
};

export function errorCode(err: unknown): string | null {
  return err && typeof err === "object" && "code" in err && typeof (err as { code?: unknown }).code === "string"
    ? (err as { code: string }).code
    : null;
}

export function apiErrorMessage(
  err: unknown,
  t: (key: string, vars?: Record<string, string | number>) => string,
): string {
  const code = errorCode(err);
  if (code && ERROR_KEYS[code]) return t(ERROR_KEYS[code]);
  return t("err.internal");
}