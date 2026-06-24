export interface PanoramaEntry {
  file: string;
  commons?: string;
}

export interface Location {
  id: string;
  lat: number;
  lon: number;
  country: string;
  region: string;
  panoramas?: PanoramaEntry[];
  panorama?: string;
  /** runtime */
  panoramaFile?: string;
  heading?: number;
  pitch?: number;
  fov?: number;
}

export interface RoundResult {
  country: string;
  region: string;
  km: number;
  score: number;
  timeBonus?: number;
}

export type DifficultyId = "easy" | "medium" | "hard" | "impossible";
export type Screen = "menu" | "difficulty" | "round" | "results" | "summary";
export type Lang = "ru" | "en" | "kk";

export interface GameSession {
  locations: Location[];
  rounds: RoundResult[];
  totalScore: number;
  difficulty: DifficultyId;
  ranked: boolean;
  roundIndex: number;
  lastGuess?: { lat: number; lon: number };
  lastKm?: number;
  lastScore?: number;
  lastBonus?: number;
}
