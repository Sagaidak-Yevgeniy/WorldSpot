const MAX_SCORE = 5000;
/** GeoGuessr decay constant in meters */
const DECAY_M = 1492.07;
const PERFECT_M = 25;

export function haversineKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371.0088; // WGS84 mean radius
  const φ1 = (lat1 * Math.PI) / 180;
  const φ2 = (lat2 * Math.PI) / 180;
  const Δφ = ((lat2 - lat1) * Math.PI) / 180;
  const Δλ = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(Δφ / 2) ** 2 + Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

/** Distance in meters (for display / scoring). */
export function haversineM(lat1: number, lon1: number, lat2: number, lon2: number): number {
  return haversineKm(lat1, lon1, lat2, lon2) * 1000;
}

/** GeoGuessr: 5000 * exp(-d / 1492.07), perfect if <= 25 m */
export function scoreFromDistanceKm(km: number): number {
  const m = km * 1000;
  if (m <= PERFECT_M) return MAX_SCORE;
  return Math.max(0, Math.round(MAX_SCORE * Math.exp(-m / DECAY_M)));
}

export function scoreFromDistanceM(m: number): number {
  if (m <= PERFECT_M) return MAX_SCORE;
  return Math.max(0, Math.round(MAX_SCORE * Math.exp(-m / DECAY_M)));
}

export function formatDistance(km: number, lang: "ru" | "en" | "kk" = "ru"): string {
  const m = km * 1000;
  const mUnit = lang === "en" ? "m" : "м";
  const kmUnit = lang === "en" ? "km" : "км";
  if (m < 1000) return `${Math.round(m)} ${mUnit}`;
  if (km < 10) return `${km.toFixed(1)} ${kmUnit}`;
  return `${Math.round(km).toLocaleString("ru-RU")} ${kmUnit}`;
}

export function formatScore(n: number): string {
  return n.toLocaleString("ru-RU");
}
