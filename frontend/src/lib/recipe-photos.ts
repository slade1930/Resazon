/** Mapa receta → foto real. Las fotos se sirven desde Cloudinary (CDN). */

const PHOTO_MAP: Record<string, string> = {
  'ARROZ CON LECHE SENCILLO': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389945/recetas/arrozconlechesencillo.jpg',
  'Arroz Con Pollo': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389946/recetas/arrozconpollo.webp',
  'BATIDO DE BANANA CON LECHE EVAPORADA': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389947/recetas/batidodebananaconlecheevaporada.png',
  'Bistec Picado con Sazón Criolla': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389948/recetas/bistecpicadoconsaz-ncriolla.jpg',
  'Canastitas de Maíz con Chorizo y Queso': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389948/recetas/canastitasdema-zconchorizo-yqueso.jpg',
  'CARLOTA DE MARACUYÁ': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389949/recetas/carlotademaracuy.jpg',
  'CHICHA DE AVENA': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389949/recetas/chichadeavena.jpg',
  'Chicheme con KLIM®': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389950/recetas/chichemepaname-oonklim.jpg',
  'CREPES CON FRUTAS': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389956/recetas/crepesconfrutas.jpg',
  'Empanadas de Jamón y Queso': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389958/recetas/empanadaspaname-asdeam-nyques.jpg',
  'Ensalada De Papas': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389959/recetas/ensaladadepapas.jpg',
  'GELATINA DE FRESA': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389961/recetas/gelatinadefresa.jpg',
  'Guacho de Patitas de Pollo': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389964/recetas/guachodepatitasdepollo.jpg',
  'Hamburguesa de Patacón con Ropa Vieja': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389965/recetas/hamburguesadepatac-nconropavieja.jpg',
  'Hojaldas': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389965/recetas/hojaldas.jpg',
  'Mamallena': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389966/recetas/mamallenapaname-a.jpg',
  'NATILLA CREMOSA': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389967/recetas/natillacremosa.jpg',
  'PALITOS O PALETAS DE BANANA CON DULCE DE LECHE': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389967/recetas/paletasdebananacondulcedeleche.webp',
  'PANCAKE DE MAÍZ DULCE': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389968/recetas/pancakedema-zdulce.jpg',
  'PANCAKES DE BANANA Y AVENA': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389969/recetas/pancakesdebananayavena.avif',
  'PUDÍN DE BANANA Y FRESA': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389970/recetas/pud-ndebananayfresa.jpg',
  'PURÉ DE PAPAS CREMOSO': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389971/recetas/pur-depapascremoso.jpg',
  'RASPADO': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389972/recetas/raspado.webp',
  'Rollos de Queso': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389972/recetas/rollosdequeso.jpg',
  'Salchichas Guisadas': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389973/recetas/salchichasguisadas.jpg',
  'Sancocho': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389973/recetas/sancocho.jpg',
  'Tamales': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389975/recetas/tamales.avif',
  'Tortillas con Queso': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389975/recetas/tortillaspaname-asconqueso.jpg',
  'VASITOS DE TRES LECHES': 'https://res.cloudinary.com/jzzpsfo1/image/upload/v1790389976/recetas/vasitosdetresleches.jpg',
};

/** Devuelve la URL de la foto de una receta, o null si no existe. */
export function recipePhotoUrl(name: string | null | undefined): string | null {
  if (!name) return null;
  const exact = PHOTO_MAP[name];
  if (exact) return exact;
  const upper = name.toUpperCase();
  for (const [key, url] of Object.entries(PHOTO_MAP)) {
    if (key.toUpperCase() === upper) return url;
  }
  return null;
}
