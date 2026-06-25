import { useCallback, useEffect, useRef, useState } from "react";
import type { DifficultyId, DuelGuessResult, DuelRoundOutcome, DuelSession, GameSession, Lang, Location, Screen } from "./types";
import { DUEL_ROUNDS, getDifficulty } from "./lib/difficulty";
import { DuelRoom, parseDuelInvite } from "./lib/duel";
import { filterAvailable, loadLocations, pickRound, poolStats } from "./lib/locations";
import { randomSeed } from "./lib/rng";
import { MenuScreen } from "./screens/MenuScreen";
import { DifficultyScreen } from "./screens/DifficultyScreen";
import { RoundScreen } from "./screens/RoundScreen";
import { ResultsScreen } from "./screens/ResultsScreen";
import { SummaryScreen } from "./screens/SummaryScreen";
import { DuelLobbyScreen } from "./screens/DuelLobbyScreen";
import { DuelRoundScreen } from "./screens/DuelRoundScreen";
import { DuelResultsScreen } from "./screens/DuelResultsScreen";
import { DuelSummaryScreen } from "./screens/DuelSummaryScreen";

function compareGuesses(my: DuelGuessResult, opp: DuelGuessResult | null): boolean | null {
  if (!opp) return true;
  if (my.score > opp.score) return true;
  if (my.score < opp.score) return false;
  if (my.km < opp.km) return true;
  if (my.km > opp.km) return false;
  if (my.elapsedMs < opp.elapsedMs) return true;
  if (my.elapsedMs > opp.elapsedMs) return false;
  return null;
}

export default function App() {
  const [screen, setScreen] = useState<Screen>("menu");
  const [lang, setLang] = useState<Lang>("ru");
  const [ranked, setRanked] = useState(false);
  const [difficulty, setDifficulty] = useState<DifficultyId>("medium");
  const [pool, setPool] = useState<Location[]>([]);
  const [session, setSession] = useState<GameSession | null>(null);

  const [duelRoom, setDuelRoom] = useState<DuelRoom | null>(null);
  const [duelSession, setDuelSession] = useState<DuelSession | null>(null);
  const [myGuess, setMyGuess] = useState<DuelGuessResult | null>(null);
  const [oppGuess, setOppGuess] = useState<DuelGuessResult | null>(null);
  const duelRoomRef = useRef<DuelRoom | null>(null);
  const duelMetaRef = useRef({ myName: "", oppName: "", isHost: false });
  const duelHandlerRooms = useRef(new WeakSet<DuelRoom>());

  const poolInfo = poolStats(pool);

  useEffect(() => {
    loadLocations().then(async (locs) => {
      const available = await filterAvailable(locs);
      setPool(available.length ? available : locs);
    });
  }, []);

  useEffect(() => {
    if (parseDuelInvite() && screen === "menu") {
      setScreen("duelLobby");
    }
  }, [screen]);

  useEffect(() => {
    return () => duelRoomRef.current?.destroy();
  }, []);

  const setupDuelRoom = useCallback(
    (room: DuelRoom) => {
      duelRoomRef.current = room;
      setDuelRoom(room);
      if (duelHandlerRooms.current.has(room)) return;
      duelHandlerRooms.current.add(room);

      room.onMessage((msg) => {
        if (msg.type === "start") {
          const meta = duelMetaRef.current;
          const locations = pickRound(pool, msg.rounds, { seed: msg.seed });
          setDuelSession({
            seed: msg.seed,
            difficulty: msg.difficulty,
            locations,
            roundIndex: 0,
            myName: meta.myName,
            oppName: meta.oppName,
            isHost: meta.isHost,
            roomId: room.roomId,
            myWins: 0,
            oppWins: 0,
            rounds: [],
            pendingOppGuess: null,
          });
          setMyGuess(null);
          setOppGuess(null);
          setScreen("duelRound");
        }

        if (msg.type === "guess") {
          setOppGuess(msg.guess);
          setDuelSession((s) => (s ? { ...s, pendingOppGuess: msg.guess } : s));
        }
      });
    },
    [pool]
  );

  const handleDuelRoomReady = useCallback(
    (room: DuelRoom, myName: string, oppName: string, isHost: boolean) => {
      duelMetaRef.current = { myName, oppName, isHost };
      setupDuelRoom(room);
    },
    [setupDuelRoom]
  );

  const startGame = useCallback(
    (diff: DifficultyId, isRanked: boolean) => {
      const cfg = getDifficulty(diff);
      const locations = pickRound(pool, cfg.rounds);
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

  const startDuel = useCallback(
    (room: DuelRoom, myName: string, oppName: string) => {
      duelMetaRef.current = { myName, oppName, isHost: true };
      setupDuelRoom(room);
      const seed = randomSeed();
      const locations = pickRound(pool, DUEL_ROUNDS, { seed });
      const ds: DuelSession = {
        seed,
        difficulty: "medium",
        locations,
        roundIndex: 0,
        myName,
        oppName,
        isHost: true,
        roomId: room.roomId,
        myWins: 0,
        oppWins: 0,
        rounds: [],
        pendingOppGuess: null,
      };
      setDuelSession(ds);
      setMyGuess(null);
      setOppGuess(null);
      room.send({ type: "start", seed, difficulty: "medium", rounds: DUEL_ROUNDS });
      setScreen("duelRound");
    },
    [pool, setupDuelRoom]
  );

  const resolveDuelRound = useCallback(
    (my: DuelGuessResult, opp: DuelGuessResult | null) => {
      if (!duelSession) return;
      const won = compareGuesses(my, opp);
      const outcome: DuelRoundOutcome = { myGuess: my, oppGuess: opp, won };
      const myWins = duelSession.myWins + (won === true ? 1 : 0);
      const oppWins = duelSession.oppWins + (won === false ? 1 : 0);
      setDuelSession({
        ...duelSession,
        myWins,
        oppWins,
        rounds: [...duelSession.rounds, outcome],
        lastOutcome: outcome,
      });
      setScreen("duelResults");
    },
    [duelSession]
  );

  useEffect(() => {
    if (!myGuess || screen !== "duelRound") return;
    if (oppGuess) {
      resolveDuelRound(myGuess, oppGuess);
    }
  }, [myGuess, oppGuess, screen, resolveDuelRound]);

  const handleDuelSubmit = (guess: DuelGuessResult) => {
    setMyGuess(guess);
    duelRoomRef.current?.send({
      type: "guess",
      roundIndex: duelSession?.roundIndex ?? 0,
      guess,
    });
    if (oppGuess) resolveDuelRound(guess, oppGuess);
  };

  const handleDuelNext = () => {
    if (!duelSession) return;
    const next = duelSession.roundIndex + 1;
    if (next >= duelSession.locations.length) {
      setScreen("duelSummary");
      return;
    }
    setDuelSession({ ...duelSession, roundIndex: next });
    setMyGuess(null);
    setOppGuess(null);
    setScreen("duelRound");
  };

  const exitDuel = () => {
    duelRoomRef.current?.destroy();
    duelRoomRef.current = null;
    setDuelRoom(null);
    setDuelSession(null);
    setMyGuess(null);
    setOppGuess(null);
    setScreen("menu");
    const url = new URL(window.location.href);
    url.searchParams.delete("duel");
    window.history.replaceState({}, "", url.pathname);
  };

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
        poolSize={poolInfo.total}
        onLang={setLang}
        onClassic={() => {
          setRanked(false);
          setScreen("difficulty");
        }}
        onRanked={() => {
          setRanked(true);
          setScreen("difficulty");
        }}
        onDuel={() => setScreen("duelLobby")}
      />
    );
  }

  if (screen === "duelLobby") {
    return (
      <DuelLobbyScreen
        lang={lang}
        poolSize={poolInfo.total}
        onLang={setLang}
        onBack={exitDuel}
        onRoomReady={(room, myName, oppName) => {
          const isGuest = !!parseDuelInvite();
          handleDuelRoomReady(room, myName, oppName, !isGuest);
        }}
        onHostStart={startDuel}
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

  if (screen === "duelRound" && duelSession && duelRoom) {
    const loc = duelSession.locations[duelSession.roundIndex];
    return (
      <DuelRoundScreen
        lang={lang}
        session={duelSession}
        location={loc}
        room={duelRoom}
        onSubmit={handleDuelSubmit}
        onMenu={exitDuel}
        oppGuessed={!!oppGuess}
        iGuessed={!!myGuess}
      />
    );
  }

  if (screen === "duelResults" && duelSession?.lastOutcome) {
    const loc = duelSession.locations[duelSession.roundIndex];
    return (
      <DuelResultsScreen
        lang={lang}
        session={duelSession}
        location={loc}
        outcome={duelSession.lastOutcome}
        onNext={handleDuelNext}
      />
    );
  }

  if (screen === "duelSummary" && duelSession) {
    return <DuelSummaryScreen lang={lang} session={duelSession} onMenu={exitDuel} />;
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
    return (
      <SummaryScreen
        lang={lang}
        session={session}
        onMenu={() => {
          setSession(null);
          setScreen("menu");
        }}
      />
    );
  }

  return null;
}
