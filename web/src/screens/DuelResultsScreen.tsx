import type { DuelRoundOutcome, DuelSession, Lang, Location } from "../types";
import { tr } from "../lib/i18n";
import { formatDistance, formatScore } from "../lib/scoring";
import { formatElapsed } from "../lib/duelScoring";
import { GameMap } from "../components/GameMap";

interface Props {
  lang: Lang;
  session: DuelSession;
  location: Location;
  outcome: DuelRoundOutcome;
  onNext: () => void;
}

export function DuelResultsScreen({ lang, session, location, outcome, onNext }: Props) {
  const { myGuess, oppGuess, won } = outcome;
  const isLast = session.roundIndex + 1 >= session.locations.length;

  return (
    <div className="screen screen--results screen--duel-results">
      <div className="duel-results__banner">
        {won === true && <h2>{tr(lang, "youWinRound")}</h2>}
        {won === false && <h2>{tr(lang, "youLoseRound")}</h2>}
        {won === null && <h2>{tr(lang, "roundDraw")}</h2>}
        <p>
          {location.country} · {location.region}
        </p>
      </div>

      <div className="duel-results__compare">
        <div className={`duel-results__player ${won === true ? "duel-results__player--win" : ""}`}>
          <h3>{session.myName}</h3>
          <p className="duel-results__dist">{formatDistance(myGuess.km, lang)}</p>
          <p className="duel-results__time">⏱ {formatElapsed(myGuess.elapsedMs)}</p>
          <p className="duel-results__pts">{formatScore(myGuess.score)} {tr(lang, "pts")}</p>
        </div>
        <div className="duel-results__vs">VS</div>
        <div className={`duel-results__player ${won === false ? "duel-results__player--win" : ""}`}>
          <h3>{session.oppName}</h3>
          {oppGuess ? (
            <>
              <p className="duel-results__dist">{formatDistance(oppGuess.km, lang)}</p>
              <p className="duel-results__time">⏱ {formatElapsed(oppGuess.elapsedMs)}</p>
              <p className="duel-results__pts">{formatScore(oppGuess.score)} {tr(lang, "pts")}</p>
            </>
          ) : (
            <p>{tr(lang, "noGuess")}</p>
          )}
        </div>
      </div>

      <div className="duel-results__map">
        <GameMap
          mapKey={`duel-res-${session.roundIndex}`}
          guess={myGuess}
          truth={{ lat: location.lat, lon: location.lon }}
          opponentGuess={oppGuess ?? undefined}
          startZoom={3}
          maxZoom={12}
          minZoom={1}
          expanded
        />
      </div>

      <div className="duel-results__scoreboard">
        {session.myName}: {session.myWins} — {session.oppWins} :{session.oppName}
      </div>

      <button type="button" className="btn-primary duel-results__next" onClick={onNext}>
        {isLast ? tr(lang, "seeResults") : tr(lang, "next")}
      </button>
    </div>
  );
}
