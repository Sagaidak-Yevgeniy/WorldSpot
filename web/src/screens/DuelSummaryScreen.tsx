import type { DuelSession, Lang } from "../types";
import { tr } from "../lib/i18n";

interface Props {
  lang: Lang;
  session: DuelSession;
  onMenu: () => void;
}

export function DuelSummaryScreen({ lang, session, onMenu }: Props) {
  const won = session.myWins > session.oppWins;
  const lost = session.myWins < session.oppWins;
  const draw = session.myWins === session.oppWins;

  return (
    <div className="screen screen--summary screen--duel-summary">
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
          <li key={i}>
            {tr(lang, "round")} {i + 1}:{" "}
            {r.won === true ? "✓" : r.won === false ? "✗" : "—"}
          </li>
        ))}
      </ul>

      <button type="button" className="btn-primary" onClick={onMenu}>
        {tr(lang, "menu")}
      </button>
    </div>
  );
}
