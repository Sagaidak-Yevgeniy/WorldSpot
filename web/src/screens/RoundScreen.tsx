import { useCallback, useEffect, useRef, useState } from "react";
import type { GameSession, Lang, Location } from "../types";
import { getDifficulty } from "../lib/difficulty";
import { tr } from "../lib/i18n";
import { panoramaUrl } from "../lib/locations";
import { haversineKm, scoreFromDistanceKm } from "../lib/scoring";
import { PanoramaView } from "../components/PanoramaView";
import { GameMap } from "../components/GameMap";
import { GuessButton } from "../components/ui";

interface Props {
  lang: Lang;
  session: GameSession;
  location: Location;
  onSubmit: (km: number, score: number, bonus: number, guess: { lat: number; lon: number }) => void;
  onMenu: () => void;
}

export function RoundScreen({ lang, session, location, onSubmit, onMenu }: Props) {
  const cfg = getDifficulty(session.difficulty);
  const [guess, setGuess] = useState<{ lat: number; lon: number } | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [ready, setReady] = useState(false);
  const [intro, setIntro] = useState(true);
  const movement = useRef(0);
  const submitted = useRef(false);
  const [timer, setTimer] = useState<number | null>(
    session.ranked && cfg.timerRanked ? cfg.timerRanked : cfg.timerCasual
  );

  const total = session.locations.length;
  const roundNum = session.roundIndex + 1;
  const src = panoramaUrl(location.panoramaFile ?? "oslo.jpg");

  const handleReady = useCallback(() => setReady(true), []);

  useEffect(() => {
    submitted.current = false;
    setGuess(null);
    setExpanded(false);
    setReady(false);
    setIntro(true);
    movement.current = 0;
    setTimer(session.ranked && cfg.timerRanked ? cfg.timerRanked : cfg.timerCasual);
    const t = setTimeout(() => setIntro(false), 1200);
    return () => clearTimeout(t);
  }, [location.id, session.ranked, cfg.timerRanked, cfg.timerCasual]);

  useEffect(() => {
    if (timer === null || !ready) return;
    const id = setInterval(() => {
      setTimer((t) => {
        if (t === null || t <= 1) {
          clearInterval(id);
          return 0;
        }
        return t - 1;
      });
    }, 1000);
    return () => clearInterval(id);
  }, [timer, ready, location.id]);

  const doSubmit = useCallback(
    (g: { lat: number; lon: number }) => {
      if (submitted.current) return;
      submitted.current = true;
      const km = haversineKm(g.lat, g.lon, location.lat, location.lon);
      let score = scoreFromDistanceKm(km);
      if (cfg.movingPenalty && movement.current > 400) score = Math.round(score * 0.65);
      score = Math.round(score * cfg.scoreMultiplier);
      let bonus = 0;
      if (timer !== null && timer > 0) {
        bonus = timer * 2;
        score += bonus;
      }
      onSubmit(km, score, bonus, g);
    },
    [location, cfg, timer, onSubmit]
  );

  useEffect(() => {
    if (timer === 0 && ready && !submitted.current) {
      const g = guess ?? { lat: 20, lon: 0 };
      doSubmit(g);
    }
  }, [timer, ready, guess, doSubmit]);

  const canGuess = !!guess && ready && !intro;

  return (
    <div className="screen screen--round">
      {intro && <div className="round__intro" />}

      <PanoramaView
        key={location.id + (location.panoramaFile ?? "")}
        src={src}
        heading={location.heading}
        pitch={location.pitch}
        zoom={55}
        allowLook={!cfg.noLook}
        allowZoom={!cfg.noLook}
        onMovement={(u) => {
          movement.current = u;
        }}
        onReady={handleReady}
      />

      <div className="hud">
        <div className="hud__left">
          <span className="hud__round">
            {tr(lang, "round")} {roundNum} / {total}
          </span>
          {cfg.showRegion && ready && (
            <span className="hud__hint">
              {tr(lang, "hintRegion")}: {location.region}
            </span>
          )}
        </div>
        <div className="hud__right">
          {session.totalScore > 0 && (
            <span className="hud__score">
              {session.totalScore.toLocaleString("ru-RU")} {tr(lang, "pts")}
            </span>
          )}
          {timer !== null && ready && <span className="hud__timer">{formatTimer(timer)}</span>}
          <button type="button" className="btn-ghost btn-ghost--sm" onClick={onMenu}>
            ✕
          </button>
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
          <button type="button" className="map-widget__expand" onClick={() => setExpanded(true)} title={tr(lang, "expandMap")}>
            ⤢
          </button>
        )}
        {expanded && (
          <button type="button" className="map-widget__close" onClick={() => setExpanded(false)}>
            × {tr(lang, "closeMap")}
          </button>
        )}
        <GameMap
          mapKey={`${location.id}-${expanded ? "x" : "m"}`}
          guess={guess}
          onGuess={(lat, lon) => setGuess({ lat, lon })}
          startZoom={cfg.startZoom}
          maxZoom={cfg.maxZoom}
          minZoom={1}
          expanded={expanded}
        />
        {!guess && ready && !intro && <p className="map-widget__hint">{tr(lang, "mapHint")}</p>}
      </div>

      <div className="round__guess">
        <GuessButton
          label={tr(lang, "guess")}
          enabled={canGuess}
          lang={lang}
          onClick={() => guess && doSubmit(guess)}
        />
      </div>
    </div>
  );
}

function formatTimer(s: number): string {
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return `${m}:${sec.toString().padStart(2, "0")}`;
}
