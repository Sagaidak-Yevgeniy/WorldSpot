import type { DifficultyId } from "../types";

export interface DifficultyConfig {
  id: DifficultyId;
  timerRanked: number | null;
  timerCasual: number | null;
  startZoom: number;
  maxZoom: number;
  scoreMultiplier: number;
  showRegion: boolean;
  showCountryAfter: boolean;
  rounds: number;
  movingPenalty: boolean;
  noLook: boolean;
}

export const DIFFICULTIES: Record<DifficultyId, DifficultyConfig> = {
  easy: {
    id: "easy",
    timerRanked: null,
    timerCasual: null,
    startZoom: 3,
    maxZoom: 12,
    scoreMultiplier: 0.9,
    showRegion: true,
    showCountryAfter: true,
    rounds: 5,
    movingPenalty: false,
    noLook: false,
  },
  medium: {
    id: "medium",
    timerRanked: 180,
    timerCasual: null,
    startZoom: 2,
    maxZoom: 15,
    scoreMultiplier: 1,
    showRegion: false,
    showCountryAfter: true,
    rounds: 5,
    movingPenalty: false,
    noLook: false,
  },
  hard: {
    id: "hard",
    timerRanked: 120,
    timerCasual: null,
    startZoom: 2,
    maxZoom: 11,
    scoreMultiplier: 1.2,
    showRegion: false,
    showCountryAfter: true,
    rounds: 5,
    movingPenalty: true,
    noLook: false,
  },
  impossible: {
    id: "impossible",
    timerRanked: 60,
    timerCasual: 75,
    startZoom: 1,
    maxZoom: 8,
    scoreMultiplier: 1.5,
    showRegion: false,
    showCountryAfter: false,
    rounds: 5,
    movingPenalty: true,
    noLook: true,
  },
};

export const DUEL_ROUNDS = 5;

export const DIFFICULTY_ORDER: DifficultyId[] = ["easy", "medium", "hard", "impossible"];

export function getDifficulty(id: DifficultyId): DifficultyConfig {
  return DIFFICULTIES[id] ?? DIFFICULTIES.medium;
}
