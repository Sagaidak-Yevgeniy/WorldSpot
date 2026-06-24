import type { VercelRequest, VercelResponse } from "@vercel/node";
import manifest from "./panorama-manifest.json";
import { proxyPanorama } from "../server/panorama";

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== "GET") {
    res.status(405).end("Method not allowed");
    return;
  }

  const id = String(req.query.id ?? "");
  const panIndex = Math.max(0, parseInt(String(req.query.n ?? "0"), 10) || 0);

  if (!id) {
    res.status(400).end("Missing id");
    return;
  }

  await proxyPanorama(id, panIndex, res, manifest as { locations: { id: string; panoramas?: { file: string; commons?: string }[] }[] });
}
