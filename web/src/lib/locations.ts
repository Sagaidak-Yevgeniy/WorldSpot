import type { Location, PanoramaEntry } from "../types";
import { fisherYates, mulberry32 } from "./rng";

const RECENT_KEY = "worldspot_recent_ids";
const RECENT_MAX = 40;

function panoramaEntries(loc: Location): PanoramaEntry[] {
  if (loc.panoramas?.length) return loc.panoramas;
  if (loc.panorama) return [{ file: loc.panorama }];
  return [];
}

export function panoramaProxyUrl(locationId: string, panIndex = 0): string {
  return `/panorama/${encodeURIComponent(locationId)}?n=${panIndex}`;
}

export interface PanoramaSources {
  /** URLs to try in order (same city, next panorama variants). */
  sources: string[];
}

export function resolvePanoramaSources(loc: Location): PanoramaSources {
  return { sources: resolvePanoramaUrlChain(loc) };
}

/** Ordered proxy URLs — current pan first, then the rest for this city. */
export function resolvePanoramaUrlChain(loc: Location): string[] {
  const entries = panoramaEntries(loc);
  const count = Math.max(entries.length, 1);
  const file = loc.panoramaFile ?? entries[0]?.file ?? "";
  let start = loc.panoramaIndex ?? entries.findIndex((p) => p.file === file);
  if (start < 0) start = 0;

  const urls: string[] = [];
  for (let i = 0; i < count; i++) {
    urls.push(panoramaProxyUrl(loc.id, (start + i) % count));
  }
  return urls;
}

export async function loadLocations(): Promise<Location[]> {
  const res = await fetch("/data/locations.json");
  const data = await res.json();
  return data.locations as Location[];
}

export async function filterAvailable(locations: Location[]): Promise<Location[]> {
  return locations;
}

function getRecentIds(): string[] {
  try {
    const raw = localStorage.getItem(RECENT_KEY);
    return raw ? (JSON.parse(raw) as string[]) : [];
  } catch {
    return [];
  }
}

function markPlayed(ids: string[]) {
  const merged = [...ids, ...getRecentIds()];
  const unique = [...new Set(merged)].slice(0, RECENT_MAX);
  localStorage.setItem(RECENT_KEY, JSON.stringify(unique));
}

function prepareLocationSeeded(loc: Location, rand: () => number): Location {
  const entries = panoramaEntries(loc);
  const panIdx = Math.floor(rand() * entries.length);
  const pan = entries[panIdx] ?? entries[0];
  return {
    ...loc,
    panoramaFile: pan?.file ?? "oslo.jpg",
    panoramaIndex: panIdx,
    heading: rand() * 360,
    pitch: (rand() - 0.5) * 24,
    fov: 72 + rand() * 20,
  };
}

export function prepareLocation(loc: Location): Location {
  return prepareLocationSeeded(loc, Math.random);
}

export interface PickRoundOptions {
  seed?: number;
  excludeIds?: string[];
}

export function pickRound(pool: Location[], count: number, options?: PickRoundOptions): Location[] {
  const recent = new Set([...getRecentIds(), ...(options?.excludeIds ?? [])]);
  let candidates = pool.filter((l) => !recent.has(l.id));
  if (candidates.length < count) candidates = [...pool];

  const rand = options?.seed !== undefined ? mulberry32(options.seed) : Math.random;
  const shuffled = fisherYates(candidates, rand);
  const picked = shuffled.slice(0, Math.min(count, shuffled.length)).map((loc, i) => {
    const r = options?.seed !== undefined ? mulberry32(options.seed! + i * 997) : Math.random;
    return prepareLocationSeeded(loc, r);
  });

  markPlayed(picked.map((p) => p.id));
  return picked;
}

/** @deprecated use resolvePanoramaSources */
export function panoramaUrl(locationId: string, panIndex = 0): string {
  return panoramaProxyUrl(locationId, panIndex);
}

export function poolStats(pool: Location[]): { total: number; regions: number } {
  const regions = new Set(pool.map((l) => l.region));
  return { total: pool.length, regions: regions.size };
}
