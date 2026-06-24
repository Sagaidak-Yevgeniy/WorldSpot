const MAX_SCORE = 5000;
const DECAY_M = 1492.07;

export function haversineKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371;
  const p = Math.PI / 180;
  const a =
    Math.sin(((lat2 - lat1) * p) / 2) ** 2 +
    Math.cos(lat1 * p) * Math.cos(lat2 * p) * Math.sin(((lon2 - lon1) * p) / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

export function scoreFromDistance(km: number): number {
  const m = km * 1000;
  if (m <= 25) return MAX_SCORE;
  return Math.max(0, Math.round(MAX_SCORE * Math.exp(-m / DECAY_M)));
}

export function formatDistance(km: number, lang: "ru" | "en" | "kk" = "ru"): string {
  const m = km * 1000;
  const mUnit = lang === "en" ? "m" : lang === "kk" ? "м" : "м";
  const kmUnit = lang === "en" ? "km" : lang === "kk" ? "км" : "км";
  if (m < 1000) return `${Math.round(m)} ${mUnit}`;
  if (km < 10) return `${km.toFixed(1)} ${kmUnit}`;
  return `${Math.round(km).toLocaleString("ru-RU")} ${kmUnit}`;
}

export function formatScore(n: number): string {
  return n.toLocaleString("ru-RU");
}
