import type { DuelSession, Lang } from "../types";
import { tr } from "../lib/i18n";
import { formatDistance, formatScore } from "../lib/scoring";
import { formatElapsed } from "../lib/duelScoring";

interface Props {
  lang: Lang;
  session: DuelSession;
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

export function DuelSummaryScreen({ lang, session, onMenu }: Props) {
  const won = session.myWins > session.oppWins;
  const lost = session.myWins < session.oppWins;
  const draw = session.myWins === session.oppWins;

  return (
    <div className="screen screen--summary screen--duel-summary">
      <MenuBackground />

      <h1>{tr(lang, "duelComplete")}</h1>

      <div className="duel-summary__result">
        {won && <p className="duel-summary__win">{tr(lang, "youWinDuel")}</p>}
        {lost && <p className="duel-summary__lose">{tr(lang, "youLoseDuel")}</p>}
        {draw && <p className="duel-summary__draw">{tr(lang, "duelDraw")}</p>}
      </div>

      <div className="duel-summary__scoreboard">
        <div className={`duel-summary__player ${won ? "duel-summary__player--win" : ""}`}>
          <span>{session.myName}</span>
          <strong>{session.myWins}</strong>
        </div>
        <span className="duel-summary__sep">—</span>
        <div className={`duel-summary__player ${lost ? "duel-summary__player--win" : ""}`}>
          <span>{session.oppName}</span>
          <strong>{session.oppWins}</strong>
        </div>
      </div>

      <ul className="duel-summary__rounds">
        {session.rounds.map((r, i) => (
          <li key={i} className="duel-summary__round">
            <span className="duel-summary__round-title">
              {tr(lang, "round")} {i + 1}
            </span>
            <span className="duel-summary__round-outcome">
              {r.won === true ? "✓" : r.won === false ? "✗" : "—"}
            </span>
            <span className="duel-summary__round-stats">
              {formatDistance(r.myGuess.km, lang)} · {formatElapsed(r.myGuess.elapsedMs)} ·{" "}
              {formatScore(r.myGuess.score)} {tr(lang, "pts")}
            </span>
          </li>
        ))}
      </ul>

      <button type="button" className="btn-primary duel-summary__menu" onClick={onMenu}>
        {tr(lang, "menu")}
      </button>
    </div>
  );
}
