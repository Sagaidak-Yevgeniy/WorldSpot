import type { GameSession, Lang } from "../types";
import { tr } from "../lib/i18n";
import { formatDistance, formatScore } from "../lib/scoring";
import { GuessButton } from "../components/ui";

interface Props {
  lang: Lang;
  session: GameSession;
  onMenu: () => void;
}

function MenuBackground() {
  return (
    <div className="menu__bg" aria-hidden>
      <div className="menu__bg-aurora" />
      <div className="menu__bg-grid" />
      <div className="menu__bg-horizon" />
      <div className="menu__bg-glow" />
    </div>
  );
}

export function SummaryScreen({ lang, session, onMenu }: Props) {
  const maxBar = Math.max(...session.rounds.map((r) => r.score), 1);
  const avgKm =
    session.rounds.length > 0
      ? session.rounds.reduce((sum, r) => sum + r.km, 0) / session.rounds.length
      : 0;

  return (
    <div className="screen screen--summary">
      <MenuBackground />

      <header className="summary__header">
        <h1>{tr(lang, "gameComplete")}</h1>
        <p className="summary__total">{formatScore(session.totalScore)}</p>
        <span className="summary__pts">{tr(lang, "pts")}</span>
        <p className="summary__meta">
          {session.rounds.length} {tr(lang, "rounds")} · {tr(lang, "summaryAvg")}{" "}
          {formatDistance(avgKm, lang)}
        </p>
      </header>

      <div className="summary__bars">
        {session.rounds.map((r, i) => (
          <div key={i} className="summary__bar-wrap">
            <div
              className="summary__bar"
              style={{ height: `${40 + (r.score / maxBar) * 120}px` }}
              title={`${r.score} ${tr(lang, "pts")}`}
            />
            <span className="summary__bar-score">{r.score}</span>
            <span className="summary__bar-label">{i + 1}</span>
          </div>
        ))}
      </div>

      <div className="summary__rounds">
        {session.rounds.map((r, i) => (
          <div key={i} className="summary__round-row">
            <span className="summary__round-num">{tr(lang, "round")} {i + 1}</span>
            <span className="summary__round-place">
              {r.country} · {r.region}
            </span>
            <span className="summary__round-km">{formatDistance(r.km, lang)}</span>
            <span className="summary__round-score">{formatScore(r.score)}</span>
          </div>
        ))}
      </div>

      <div className="summary__play">
        <GuessButton label={tr(lang, "menu")} enabled lang={lang} onClick={onMenu} />
      </div>
    </div>
  );
}
