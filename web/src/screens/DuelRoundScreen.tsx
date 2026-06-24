import { useCallback, useEffect, useRef, useState } from "react";
import type { DuelSession, Lang, Location } from "../types";
import { tr } from "../lib/i18n";
import { resolvePanoramaSources } from "../lib/locations";
import { haversineKm } from "../lib/scoring";
import { duelRoundScore, duelTimeLimitMs } from "../lib/duelScoring";
import type { DuelRoom } from "../lib/duel";
import { PanoramaView } from "../components/PanoramaView";
import { GameMap } from "../components/GameMap";
import { GuessButton } from "../components/ui";

interface Props {
  lang: Lang;
  session: DuelSession;
  location: Location;
  room: DuelRoom;
  onSubmit: (guess: {
    lat: number;
    lon: number;
    elapsedMs: number;
    km: number;
    score: number;
  }) => void;
  onMenu: () => void;
  oppGuessed: boolean;
  iGuessed: boolean;
}

export function DuelRoundScreen({
  lang,
  session,
  location,
  room: _room,
  onSubmit,
  onMenu,
  oppGuessed,
  iGuessed,
}: Props) {
  const [guess, setGuess] = useState<{ lat: number; lon: number } | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [ready, setReady] = useState(false);
  const [intro, setIntro] = useState(true);
  const startMs = useRef(Date.now());
  const submitted = useRef(false);
  const [elapsed, setElapsed] = useState(0);
  const pano = resolvePanoramaSources(location);
  const total = session.locations.length;
  const roundNum = session.roundIndex + 1;
  const timeLimit = duelTimeLimitMs();

  useEffect(() => {
    submitted.current = false;
    setGuess(null);
    setExpanded(false);
    setReady(false);
    setIntro(true);
    startMs.current = Date.now();
    const t = setTimeout(() => setIntro(false), 800);
    return () => clearTimeout(t);
  }, [location.id]);

  useEffect(() => {
    if (!ready || iGuessed) return;
    const id = setInterval(() => {
      const ms = Date.now() - startMs.current;
      setElapsed(ms);
      if (ms >= timeLimit && !submitted.current) {
        const g = guess ?? { lat: 0, lon: 0 };
        doSubmit(g);
      }
    }, 50);
    return () => clearInterval(id);
  }, [ready, iGuessed, guess, timeLimit]);

  const doSubmit = useCallback(
    (g: { lat: number; lon: number }) => {
      if (submitted.current) return;
      submitted.current = true;
      const elapsedMs = Date.now() - startMs.current;
      const km = haversineKm(g.lat, g.lon, location.lat, location.lon);
      const score = duelRoundScore(km, elapsedMs);
      onSubmit({ lat: g.lat, lon: g.lon, elapsedMs, km, score });
    },
    [location, onSubmit]
  );

  const canGuess = !!guess && ready && !intro && !iGuessed;
  const timeLeft = Math.max(0, timeLimit - elapsed);

  return (
    <div className="screen screen--round screen--duel-round">
      {intro && <div className="round__intro" />}

      <PanoramaView
        key={location.id + String(location.panoramaIndex ?? 0)}
        sources={pano.sources}
        heading={location.heading}
        pitch={location.pitch}
        zoom={55}
        allowLook
        allowZoom
        onReady={() => setReady(true)}
      />

      <div className="hud hud--duel">
        <div className="hud__left">
          <span className="hud__round">
            {tr(lang, "round")} {roundNum} / {total}
          </span>
          <span className="hud__duel-score">
            {session.myWins} — {session.oppWins}
          </span>
        </div>
        <div className="hud__right">
          <span className="hud__timer">{formatMs(timeLeft)}</span>
          <button type="button" className="btn-ghost btn-ghost--sm" onClick={onMenu}>
            ✕
          </button>
        </div>
      </div>

      <div className="duel-status-bar">
        <div className={`duel-status ${iGuessed ? "duel-status--done" : ""}`}>
          <span>{session.myName}</span>
          <small>{iGuessed ? tr(lang, "guessed") : tr(lang, "thinking")}</small>
        </div>
        <div className={`duel-status ${oppGuessed ? "duel-status--done" : ""}`}>
          <span>{session.oppName}</span>
          <small>{oppGuessed ? tr(lang, "guessed") : tr(lang, "thinking")}</small>
        </div>
      </div>

      {!ready && (
        <div className="round__loading">
          <div className="panorama__loader" />
          <p>{tr(lang, "loading")}</p>
        </div>
      )}

      {expanded && <div className="map-overlay" onClick={() => setExpanded(false)} role="presentation" />}

      <div className={`map-widget ${expanded ? "map-widget--expanded" : ""}`}>
        {!expanded && (
          <button type="button" className="map-widget__expand" onClick={() => setExpanded(true)}>
            ⤢
          </button>
        )}
        {expanded && (
          <button type="button" className="map-widget__close" onClick={() => setExpanded(false)}>
            × {tr(lang, "closeMap")}
          </button>
        )}
        <GameMap
          mapKey={`duel-${location.id}`}
          guess={guess}
          onGuess={(lat, lon) => !iGuessed && setGuess({ lat, lon })}
          startZoom={2}
          maxZoom={15}
          minZoom={1}
          expanded={expanded}
        />
        {!guess && ready && !intro && !iGuessed && (
          <p className="map-widget__hint">{tr(lang, "mapHint")}</p>
        )}
      </div>

      <div className="round__guess">
        <GuessButton
          label={iGuessed ? tr(lang, "waitingOpponent") : tr(lang, "guess")}
          enabled={canGuess}
          lang={lang}
          onClick={() => guess && doSubmit(guess)}
        />
      </div>
    </div>
  );
}

function formatMs(ms: number): string {
  const s = Math.ceil(ms / 1000);
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return `${m}:${sec.toString().padStart(2, "0")}`;
}
