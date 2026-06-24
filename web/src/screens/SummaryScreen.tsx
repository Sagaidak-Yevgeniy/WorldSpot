import type { GameSession, Lang } from "../types";
import { tr } from "../lib/i18n";
import { formatScore } from "../lib/scoring";
import { GuessButton } from "../components/ui";

interface Props {
  lang: Lang;
  session: GameSession;
  onMenu: () => void;
}

export function SummaryScreen({ lang, session, onMenu }: Props) {
  const maxBar = Math.max(...session.rounds.map((r) => r.score), 1);

  return (
    <div className="screen screen--summary">
      <div className="menu__bg" />
      <header className="summary__header">
        <h1>{tr(lang, "gameComplete")}</h1>
        <p className="summary__total">{formatScore(session.totalScore)}</p>
        <span className="summary__pts">{tr(lang, "pts")}</span>
      </header>

      <div className="summary__bars">
        {session.rounds.map((r, i) => (
          <div key={i} className="summary__bar-wrap">
            <div
              className="summary__bar"
              style={{ height: `${40 + (r.score / maxBar) * 120}px` }}
              title={`${r.score} pts`}
            />
            <span className="summary__bar-score">{r.score}</span>
            <span className="summary__bar-label">{r.country.slice(0, 6)}</span>
          </div>
        ))}
      </div>

      <div className="summary__play">
        <GuessButton label={tr(lang, "menu")} enabled lang={lang} onClick={onMenu} />
      </div>
    </div>
  );
}
