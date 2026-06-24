#!/usr/bin/env python3
"""Sync location data for web: public JSON without commons + API manifest."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "locations.json"
PUBLIC = ROOT / "web" / "public" / "data" / "locations.json"
MANIFEST = ROOT / "web" / "api" / "panorama-manifest.json"
WEB_PANORAMAS = ROOT / "web" / "public" / "panoramas"
ASSETS_PANORAMAS = ROOT / "assets" / "panoramas"


def strip_for_client(loc: dict) -> dict:
    out = {k: v for k, v in loc.items() if k != "panoramas"}
    pans = loc.get("panoramas", [])
    if pans:
        out["panoramas"] = [{"file": p["file"]} for p in pans]
    return out


def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)

    public = {"locations": [strip_for_client(loc) for loc in data["locations"]]}
    PUBLIC.write_text(json.dumps(public, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False) + "\n", encoding="utf-8")

    WEB_PANORAMAS.mkdir(parents=True, exist_ok=True)
    if ASSETS_PANORAMAS.exists():
        for f in ASSETS_PANORAMAS.glob("*.jpg"):
            shutil.copy2(f, WEB_PANORAMAS / f.name)

    print(f"Public: {len(public['locations'])} cities (no commons in HTML/JSON)")
    print(f"Manifest: {MANIFEST}")


if __name__ == "__main__":
    main()
