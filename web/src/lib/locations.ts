import type { Location } from "../types";

function panoramaEntries(loc: Location) {
  if (loc.panoramas?.length) return loc.panoramas;
  if (loc.panorama) return [{ file: loc.panorama }];
  return [];
}

export async function loadLocations(): Promise<Location[]> {
  const res = await fetch("/data/locations.json");
  const data = await res.json();
  return data.locations as Location[];
}

export async function filterAvailable(locations: Location[]): Promise<Location[]> {
  const checks = await Promise.all(
    locations.map(async (loc) => {
      for (const p of panoramaEntries(loc)) {
        try {
          const r = await fetch(`/panoramas/${p.file}`, { method: "HEAD" });
          if (r.ok) return true;
        } catch {
          /* ignore */
        }
      }
      return false;
    })
  );
  return locations.filter((_, i) => checks[i]);
}

export function prepareLocation(loc: Location): Location {
  const entries = panoramaEntries(loc);
  const pan = entries[Math.floor(Math.random() * entries.length)];
  return {
    ...loc,
    panoramaFile: pan?.file ?? "placeholder.jpg",
    heading: Math.random() * 360,
    pitch: (Math.random() - 0.5) * 36,
    fov: 72 + Math.random() * 26,
  };
}

export function pickRound(pool: Location[], count: number): Location[] {
  const shuffled = [...pool].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, Math.min(count, shuffled.length)).map(prepareLocation);
}

export function panoramaUrl(file: string): string {
  return `/panoramas/${file}`;
}
