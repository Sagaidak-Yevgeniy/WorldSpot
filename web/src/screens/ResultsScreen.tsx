import { useEffect, useState } from "react";
import type { GameSession, Lang, Location } from "../types";
import { getDifficulty } from "../lib/difficulty";
import { tr } from "../lib/i18n";
import { formatDistance, formatScore } from "../lib/scoring";
import { GameMap } from "../components/GameMap";
import { GuessButton } from "../components/ui";

interface Props {
  lang: Lang;
  session: GameSession;
  location: Location;
  km: number;
  score: number;
  bonus: number;
  onNext: () => void;
}

export function ResultsScreen({ lang, session, location, km, score, bonus, onNext }: Props) {
  const cfg = getDifficulty(session.difficulty);
  const [anim, setAnim] = useState(0);
  const guess = session.lastGuess!;
  const isLast = session.roundIndex + 1 >= session.locations.length;

  useEffect(() => {
    let start: number | null = null;
    const dur = 1600;
    const step = (ts: number) => {
      if (!start) start = ts;
      const t = Math.min(1, (ts - start) / dur);
      const ease = 1 - (1 - t) ** 3;
      setAnim(Math.round(score * ease));
      if (t < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [score]);

  return (
    <div className="screen screen--results">
      <div className="hud">
        <span className="hud__round">
          {tr(lang, "round")} {session.roundIndex + 1} / {session.locations.length}
        </span>
        <span className="hud__score">
          {formatScore(session.totalScore)} {tr(lang, "pts")}
        </span>
      </div>

      <div className="results__panel">
        <p className="results__distance">{formatDistance(km, lang)}</p>
        <p className="results__score">
          {formatScore(anim)} {tr(lang, "pts")}
          {bonus > 0 && <span className="results__bonus"> +{bonus}</span>}
        </p>
        {cfg.showCountryAfter && (
          <p className="results__place">
            {location.country} — {location.region}
          </p>
        )}
      </div>

      <div className="results__map">
        <GameMap
          guess={guess}
          truth={{ lat: location.lat, lon: location.lon }}
          startZoom={3}
          maxZoom={14}
          expanded
        />
      </div>

      <div className="round__guess">
        <GuessButton
          label={isLast ? tr(lang, "seeResults") : tr(lang, "next")}
          enabled
          lang={lang}
          onClick={onNext}
        />
      </div>
    </div>
  );
}
