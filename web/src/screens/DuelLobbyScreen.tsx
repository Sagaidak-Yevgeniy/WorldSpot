import { useEffect, useState } from "react";
import type { Lang } from "../types";
import { tr } from "../lib/i18n";
import { DuelRoom, copyInviteLink, duelInviteUrl, parseDuelInvite } from "../lib/duel";
import { LangToggle } from "../components/ui";

interface Props {
  lang: Lang;
  poolSize: number;
  onLang: (l: Lang) => void;
  onBack: () => void;
  onRoomReady: (room: DuelRoom, myName: string, oppName: string) => void;
  onHostStart: (room: DuelRoom, myName: string, oppName: string) => void;
}

export function DuelLobbyScreen({ lang, poolSize, onLang, onBack, onRoomReady, onHostStart }: Props) {
  const inviteCode = parseDuelInvite();
  const isGuest = !!inviteCode;
  const [name, setName] = useState("");
  const [room, setRoom] = useState<DuelRoom | null>(null);
  const [status, setStatus] = useState<"idle" | "connecting" | "waiting" | "ready" | "error">("idle");
  const [oppName, setOppName] = useState("");
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    return () => room?.destroy();
  }, [room]);

  const connect = async () => {
    if (!name.trim()) return;
    setStatus("connecting");
    setError("");
    try {
      const r = new DuelRoom(isGuest ? "guest" : "host", inviteCode ?? undefined);
      r.onMessage((msg) => {
        if (msg.type === "hello") {
          setOppName(msg.name);
          setStatus("ready");
          r.send({ type: "hello", name: name.trim() });
          onRoomReady(r, name.trim(), msg.name);
        }
      });
      await r.connect();
      setRoom(r);
      r.send({ type: "hello", name: name.trim() });
      setStatus(isGuest ? "waiting" : "waiting");
      if (isGuest) {
        // guest waits for host start — host will appear via hello echo if host sends first
      }
    } catch {
      setStatus("error");
      setError(tr(lang, "duelConnectError"));
    }
  };

  const handleCopy = async () => {
    if (!room) return;
    const ok = await copyInviteLink(room.roomId);
    setCopied(ok);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleStart = () => {
    if (!room || !oppName) return;
    onHostStart(room, name.trim(), oppName);
  };

  return (
    <div className="screen screen--duel-lobby">
      <LangToggle lang={lang} onChange={onLang} />
      <button type="button" className="btn-ghost duel-lobby__back" onClick={onBack}>
        ← {tr(lang, "back")}
      </button>

      <div className="duel-lobby__card">
        <span className="duel-lobby__icon">⚔️</span>
        <h1>{tr(lang, "duel")}</h1>
        <p className="duel-lobby__desc">{tr(lang, "duelDesc")}</p>
        <p className="duel-lobby__pool">
          {poolSize}+ {tr(lang, "citiesInPool")}
        </p>

        {status === "idle" && (
          <>
            <label className="duel-lobby__label">
              {tr(lang, "yourName")}
              <input
                type="text"
                maxLength={20}
                placeholder={tr(lang, "namePlaceholder")}
                value={name}
                onChange={(e) => setName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && connect()}
              />
            </label>
            <button type="button" className="btn-primary" disabled={!name.trim()} onClick={connect}>
              {isGuest ? tr(lang, "joinDuel") : tr(lang, "createDuel")}
            </button>
          </>
        )}

        {status === "connecting" && (
          <div className="duel-lobby__status">
            <div className="panorama__loader" />
            <p>{tr(lang, "connecting")}</p>
          </div>
        )}

        {(status === "waiting" || status === "ready") && room && (
          <>
            <div className="duel-lobby__room">
              <span className="duel-lobby__code-label">{tr(lang, "roomCode")}</span>
              <code className="duel-lobby__code">{room.roomId}</code>
            </div>

            {!isGuest && (
              <div className="duel-lobby__invite">
                <input readOnly value={duelInviteUrl(room.roomId)} className="duel-lobby__link" />
                <button type="button" className="btn-secondary" onClick={handleCopy}>
                  {copied ? tr(lang, "copied") : tr(lang, "inviteFriend")}
                </button>
              </div>
            )}

            <div className="duel-lobby__players">
              <div className="duel-player duel-player--you">
                <span>{name}</span>
                <small>{tr(lang, "you")}</small>
              </div>
              <span className="duel-lobby__vs">VS</span>
              <div className={`duel-player ${oppName ? "" : "duel-player--empty"}`}>
                <span>{oppName || "…"}</span>
                <small>{oppName ? tr(lang, "opponent") : tr(lang, "waitingOpponent")}</small>
              </div>
            </div>

            {!isGuest && (
              <button
                type="button"
                className="btn-primary"
                disabled={!oppName}
                onClick={handleStart}
              >
                {tr(lang, "startDuel")}
              </button>
            )}

            {isGuest && (
              <p className="duel-lobby__hint">{tr(lang, "waitHostStart")}</p>
            )}
          </>
        )}

        {status === "error" && (
          <>
            <p className="duel-lobby__error">{error}</p>
            <button type="button" className="btn-secondary" onClick={() => setStatus("idle")}>
              {tr(lang, "retry")}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
