import { useCallback, useEffect, useState } from "react";
import type { DifficultyId, GameSession, Lang, Location, Screen } from "./types";
import { getDifficulty } from "./lib/difficulty";
import { filterAvailable, loadLocations, pickRound } from "./lib/locations";
import { MenuScreen } from "./screens/MenuScreen";
import { DifficultyScreen } from "./screens/DifficultyScreen";
import { RoundScreen } from "./screens/RoundScreen";
import { ResultsScreen } from "./screens/ResultsScreen";
import { SummaryScreen } from "./screens/SummaryScreen";

export default function App() {
  const [screen, setScreen] = useState<Screen>("menu");
  const [lang, setLang] = useState<Lang>("ru");
  const [ranked, setRanked] = useState(false);
  const [difficulty, setDifficulty] = useState<DifficultyId>("medium");
  const [pool, setPool] = useState<Location[]>([]);
  const [session, setSession] = useState<GameSession | null>(null);

  useEffect(() => {
    loadLocations().then(async (locs) => {
      const available = await filterAvailable(locs);
      setPool(available.length ? available : locs);
    });
  }, []);

  const startGame = useCallback(
    async (diff: DifficultyId, isRanked: boolean) => {
      const cfg = getDifficulty(diff);
      const locations = await pickRound(pool, cfg.rounds);
      setSession({
        locations,
        rounds: [],
        totalScore: 0,
        difficulty: diff,
        ranked: isRanked,
        roundIndex: 0,
      });
      setScreen("round");
    },
    [pool]
  );

  const handleSubmit = (km: number, score: number, bonus: number, guess: { lat: number; lon: number }) => {
    if (!session) return;
    const loc = session.locations[session.roundIndex];
    setSession({
      ...session,
      totalScore: session.totalScore + score,
      rounds: [
        ...session.rounds,
        { country: loc.country, region: loc.region, km: Math.round(km * 10) / 10, score, timeBonus: bonus },
      ],
      lastGuess: guess,
      lastKm: km,
      lastScore: score,
      lastBonus: bonus,
    });
    setScreen("results");
  };

  const handleNext = () => {
    if (!session) return;
    const next = session.roundIndex + 1;
    if (next >= session.locations.length) {
      setScreen("summary");
      return;
    }
    setSession({ ...session, roundIndex: next });
    setScreen("round");
  };

  if (screen === "menu") {
    return (
      <MenuScreen
        lang={lang}
        onLang={setLang}
        onClassic={() => {
          setRanked(false);
          setScreen("difficulty");
        }}
        onRanked={() => {
          setRanked(true);
          setScreen("difficulty");
        }}
      />
    );
  }

  if (screen === "difficulty") {
    return (
      <DifficultyScreen
        lang={lang}
        ranked={ranked}
        selected={difficulty}
        onSelect={setDifficulty}
        onPlay={() => startGame(difficulty, ranked)}
        onBack={() => setScreen("menu")}
        onLang={setLang}
      />
    );
  }

  if (!session) {
    return (
      <div className="screen screen--loading-app">
        <div className="panorama__loader" />
      </div>
    );
  }

  const loc = session.locations[session.roundIndex];

  if (screen === "round") {
    return (
      <RoundScreen
        lang={lang}
        session={session}
        location={loc}
        onSubmit={handleSubmit}
        onMenu={() => setScreen("menu")}
      />
    );
  }

  if (screen === "results" && session.lastKm !== undefined && session.lastGuess) {
    return (
      <ResultsScreen
        lang={lang}
        session={session}
        location={loc}
        km={session.lastKm}
        score={session.lastScore ?? 0}
        bonus={session.lastBonus ?? 0}
        onNext={handleNext}
      />
    );
  }

  if (screen === "summary") {
    return <SummaryScreen lang={lang} session={session} onMenu={() => setScreen("menu")} />;
  }

  return null;
}
