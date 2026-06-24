import type { IncomingMessage, ServerResponse } from "node:http";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { resolve, dirname } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));

interface PanEntry {
  file: string;
  commons?: string;
}

interface LocEntry {
  id: string;
  panoramas?: PanEntry[];
}

interface Manifest {
  locations: LocEntry[];
}

const UA = "WorldSpot/1.0 (educational geography game)";

function loadManifest(): Manifest {
  const p = resolve(__dirname, "../api/panorama-manifest.json");
  return JSON.parse(readFileSync(p, "utf-8")) as Manifest;
}

function commonsUrl(title: string, width = 2560): string {
  const name = title.trim().replace(/ /g, "_");
  return `https://commons.wikimedia.org/wiki/Special:FilePath/${encodeURIComponent(name)}?width=${width}`;
}

function resolveImageUrl(id: string, panIndex: number, manifest: Manifest): string | null {
  const loc = manifest.locations.find((l) => l.id === id);
  if (!loc?.panoramas?.length) return null;
  const pan = loc.panoramas[panIndex] ?? loc.panoramas[0];
  if (!pan?.commons) return null;
  return commonsUrl(pan.commons);
}

export async function proxyPanorama(
  id: string,
  startPanIndex: number,
  res: ServerResponse,
  manifest: Manifest
): Promise<void> {
  const loc = manifest.locations.find((l) => l.id === id);
  const panCount = loc?.panoramas?.length ?? 0;
  if (!panCount) {
    res.statusCode = 404;
    res.end("Not found");
    return;
  }

  for (let attempt = 0; attempt < panCount; attempt++) {
    const panIndex = (startPanIndex + attempt) % panCount;
    const url = resolveImageUrl(id, panIndex, manifest);
    if (!url) continue;

    try {
      const upstream = await fetch(url, { headers: { "User-Agent": UA }, redirect: "follow" });
      if (!upstream.ok) continue;

      const ct = upstream.headers.get("content-type") ?? "image/jpeg";
      const buf = Buffer.from(await upstream.arrayBuffer());
      if (buf.length < 50_000) continue;

      res.statusCode = 200;
      res.setHeader("Content-Type", ct);
      res.setHeader("Cache-Control", "public, max-age=86400");
      res.end(buf);
      return;
    } catch {
      continue;
    }
  }

  res.statusCode = 404;
  res.end("Not found");
}

/** Vite dev middleware handler mounted at /panorama */
export function panoramaMiddleware(
  req: IncomingMessage,
  res: ServerResponse,
  next: () => void
): void {
  if (!req.url || req.method !== "GET") {
    next();
    return;
  }

  const raw = req.url.split("?")[0] ?? "";
  const id = decodeURIComponent(raw.replace(/^\//, ""));
  if (!id) {
    next();
    return;
  }

  const qs = new URL(req.url, "http://x").searchParams;
  const panIndex = Math.max(0, parseInt(qs.get("n") ?? "0", 10) || 0);

  let manifest: Manifest;
  try {
    manifest = loadManifest();
  } catch {
    res.statusCode = 500;
    res.end("Manifest missing");
    return;
  }

  proxyPanorama(id, panIndex, res, manifest).catch(() => {
    if (!res.headersSent) {
      res.statusCode = 502;
      res.end("Proxy error");
    }
  });
}
