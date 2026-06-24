import { scoreFromDistanceKm } from "./scoring";

const DUEL_TIME_MS = 120_000;

/** GeoGuessr-style duel score: distance + speed bonus. */
export function duelRoundScore(km: number, elapsedMs: number): number {
  const dist = scoreFromDistanceKm(km);
  const speedBonus = Math.round(Math.max(0, (DUEL_TIME_MS - elapsedMs) / DUEL_TIME_MS) * 1200);
  return dist + speedBonus;
}

export function duelTimeLimitMs(): number {
  return DUEL_TIME_MS;
}

export function formatElapsed(ms: number): string {
  const s = Math.floor(ms / 1000);
  const m = Math.floor(s / 60);
  const sec = s % 60;
  const cs = Math.floor((ms % 1000) / 10);
  if (m > 0) return `${m}:${sec.toString().padStart(2, "0")}.${cs.toString().padStart(2, "0")}`;
  return `${sec}.${cs.toString().padStart(2, "0")}s`;
}
