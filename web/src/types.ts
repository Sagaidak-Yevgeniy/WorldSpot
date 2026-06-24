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
  panoramaIndex?: number;
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
export type Screen =
  | "menu"
  | "difficulty"
  | "round"
  | "results"
  | "summary"
  | "duelLobby"
  | "duelRound"
  | "duelResults"
  | "duelSummary";
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

export interface DuelGuessResult {
  lat: number;
  lon: number;
  elapsedMs: number;
  km: number;
  score: number;
}

export interface DuelRoundOutcome {
  myGuess: DuelGuessResult;
  oppGuess: DuelGuessResult | null;
  won: boolean | null;
}

export interface DuelSession {
  seed: number;
  difficulty: DifficultyId;
  locations: Location[];
  roundIndex: number;
  myName: string;
  oppName: string;
  isHost: boolean;
  roomId: string;
  myWins: number;
  oppWins: number;
  rounds: DuelRoundOutcome[];
  pendingOppGuess: DuelGuessResult | null;
  lastOutcome?: DuelRoundOutcome;
}
