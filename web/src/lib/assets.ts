/** Resolve path relative to Vite base (e.g. /world-spot/). */
export function assetUrl(path: string): string {
  const clean = path.startsWith("/") ? path.slice(1) : path;
  const base = import.meta.env.BASE_URL;
  return `${base}${clean}`;
}
