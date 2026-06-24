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

/** Check which panorama files exist (GET tiny range — works when HEAD is blocked). */
export async function filterAvailable(locations: Location[]): Promise<Location[]> {
  const checkFile = (file: string): Promise<boolean> =>
    new Promise((resolve) => {
      const img = new Image();
      img.onload = () => resolve(true);
      img.onerror = () => resolve(false);
      img.src = `/panoramas/${file}?t=${Date.now()}`;
    });

  const results = await Promise.all(
    locations.map(async (loc) => {
      for (const p of panoramaEntries(loc)) {
        if (await checkFile(p.file)) return true;
      }
      return false;
    })
  );

  const available = locations.filter((_, i) => results[i]);
  return available.length > 0 ? available : locations;
}

export function prepareLocation(loc: Location, availableFiles?: Set<string>): Location {
  const entries = panoramaEntries(loc);
  let pool = entries;
  if (availableFiles) {
    pool = entries.filter((e) => availableFiles.has(e.file));
  }
  if (!pool.length) pool = entries;
  const pan = pool[Math.floor(Math.random() * pool.length)];
  return {
    ...loc,
    panoramaFile: pan?.file ?? entries[0]?.file ?? "oslo.jpg",
    heading: Math.random() * 360,
    pitch: (Math.random() - 0.5) * 24,
    fov: 72 + Math.random() * 20,
  };
}

export async function pickRound(pool: Location[], count: number): Promise<Location[]> {
  const availableFiles = new Set<string>();
  await Promise.all(
    pool.flatMap((loc) =>
      panoramaEntries(loc).map(async (p) => {
        const ok = await new Promise<boolean>((res) => {
          const img = new Image();
          img.onload = () => res(true);
          img.onerror = () => res(false);
          img.src = `/panoramas/${p.file}`;
        });
        if (ok) availableFiles.add(p.file);
      })
    )
  );

  const withPhotos = pool.filter((loc) =>
    panoramaEntries(loc).some((p) => availableFiles.has(p.file))
  );
  const source = withPhotos.length ? withPhotos : pool;
  const shuffled = [...source].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, Math.min(count, shuffled.length)).map((loc) => prepareLocation(loc, availableFiles));
}

export function panoramaUrl(file: string): string {
  return `/panoramas/${encodeURIComponent(file)}`;
}
