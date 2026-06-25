import type { IncomingMessage, ServerResponse } from "node:http";
import { readFileSync, existsSync, statSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { resolve, dirname } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PUBLIC_PANORAMAS = resolve(__dirname, "../public/panoramas");

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

const UA = "WorldSpot/1.0 (educational geography game; github.com/Sagaidak-Yevgeniy/WorldSpot)";
const MIN_BYTES = 15_000;

function loadManifest(): Manifest {
  const p = resolve(__dirname, "../api/panorama-manifest.json");
  return JSON.parse(readFileSync(p, "utf-8")) as Manifest;
}

function readLocalPanorama(file: string): Buffer | null {
  const safe = file.replace(/[/\\]/g, "");
  const p = resolve(PUBLIC_PANORAMAS, safe);
  if (!p.startsWith(PUBLIC_PANORAMAS)) return null;
  if (!existsSync(p)) return null;
  const size = statSync(p).size;
  if (size < MIN_BYTES) return null;
  return readFileSync(p);
}

async function commonsThumbUrl(title: string, width = 2560): Promise<string | null> {
  const params = new URLSearchParams({
    action: "query",
    titles: `File:${title}`,
    prop: "imageinfo",
    iiprop: "url",
    iiurlwidth: String(width),
    format: "json",
  });
  const resp = await fetch(`https://commons.wikimedia.org/w/api.php?${params}`, {
    headers: { "User-Agent": UA },
  });
  if (!resp.ok) return null;
  const data = (await resp.json()) as {
    query?: { pages?: Record<string, { missing?: boolean; imageinfo?: { thumburl?: string; url?: string }[] }> };
  };
  const page = Object.values(data.query?.pages ?? {})[0];
  if (!page || page.missing) return null;
  const info = page.imageinfo?.[0];
  return info?.thumburl ?? info?.url ?? null;
}

async function fetchRemote(url: string): Promise<Buffer | null> {
  try {
    const upstream = await fetch(url, { headers: { "User-Agent": UA }, redirect: "follow" });
    if (!upstream.ok) return null;
    const buf = Buffer.from(await upstream.arrayBuffer());
    return buf.length >= MIN_BYTES ? buf : null;
  } catch {
    return null;
  }
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
    const pan = loc!.panoramas![panIndex];
    if (!pan) continue;

    const local = readLocalPanorama(pan.file);
    if (local) {
      res.statusCode = 200;
      res.setHeader("Content-Type", "image/jpeg");
      res.setHeader("Cache-Control", "public, max-age=86400");
      res.end(local);
      return;
    }

    if (pan.commons) {
      const thumb = await commonsThumbUrl(pan.commons);
      if (thumb) {
        const remote = await fetchRemote(thumb);
        if (remote) {
          res.statusCode = 200;
          res.setHeader("Content-Type", "image/jpeg");
          res.setHeader("Cache-Control", "public, max-age=3600");
          res.end(remote);
          return;
        }
      }
    }
  }

  res.statusCode = 404;
  res.end("Not found");
}

/** Vite dev/preview middleware mounted at /panorama */
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
