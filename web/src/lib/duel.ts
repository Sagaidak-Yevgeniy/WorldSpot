import type { DataConnection } from "peerjs";
import Peer from "peerjs";
import type { DifficultyId } from "../types";
import { randomSeed } from "./rng";

export type DuelRole = "host" | "guest";

export interface DuelGuess {
  lat: number;
  lon: number;
  elapsedMs: number;
  km: number;
  score: number;
}

export type DuelMessage =
  | { type: "hello"; name: string }
  | { type: "start"; seed: number; difficulty: DifficultyId; rounds: number }
  | { type: "guess"; roundIndex: number; guess: DuelGuess }
  | { type: "ping" };

export interface DuelPeerState {
  connected: boolean;
  opponentName: string;
  role: DuelRole;
  roomId: string;
}

type MsgHandler = (msg: DuelMessage) => void;

function makeRoomId(): string {
  const part = Math.random().toString(36).slice(2, 8).toUpperCase();
  return `WS-${part}`;
}

export class DuelRoom {
  private peer: Peer | null = null;
  private conn: DataConnection | null = null;
  private handler: MsgHandler | null = null;
  readonly roomId: string;
  readonly role: DuelRole;

  constructor(role: DuelRole, roomId?: string) {
    this.role = role;
    this.roomId = roomId ?? makeRoomId();
  }

  onMessage(handler: MsgHandler) {
    this.handler = handler;
  }

  private emit(msg: DuelMessage) {
    this.handler?.(msg);
  }

  private bindConn(conn: DataConnection) {
    this.conn = conn;
    conn.on("data", (raw) => {
      const msg = raw as DuelMessage;
      if (msg?.type) this.emit(msg);
    });
    conn.on("close", () => {
      this.conn = null;
    });
  }

  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      const peerId = this.role === "host" ? this.roomId : `${this.roomId}-guest-${randomSeed()}`;
      this.peer = new Peer(peerId, {
        debug: 0,
      });

      const timeout = window.setTimeout(() => reject(new Error("peer_timeout")), 20000);

      this.peer.on("open", () => {
        window.clearTimeout(timeout);
        if (this.role === "guest") {
          const hostConn = this.peer!.connect(this.roomId, { reliable: true });
          hostConn.on("open", () => {
            this.bindConn(hostConn);
            resolve();
          });
          hostConn.on("error", reject);
        } else {
          this.peer!.on("connection", (incoming) => {
            if (this.conn?.open) return;
            incoming.on("open", () => {
              this.bindConn(incoming);
            });
          });
          resolve();
        }
      });

      this.peer.on("error", (err) => {
        window.clearTimeout(timeout);
        reject(err);
      });
    });
  }

  send(msg: DuelMessage) {
    if (this.conn?.open) this.conn.send(msg);
  }

  destroy() {
    this.conn?.close();
    this.peer?.destroy();
    this.conn = null;
    this.peer = null;
  }

  get isConnected() {
    return !!this.conn?.open;
  }
}

export function duelInviteUrl(roomId: string): string {
  const url = new URL(window.location.href);
  url.searchParams.set("duel", roomId);
  return url.toString();
}

export function parseDuelInvite(): string | null {
  const params = new URLSearchParams(window.location.search);
  return params.get("duel");
}

export async function copyInviteLink(roomId: string): Promise<boolean> {
  const link = duelInviteUrl(roomId);
  try {
    await navigator.clipboard.writeText(link);
    return true;
  } catch {
    return false;
  }
}
