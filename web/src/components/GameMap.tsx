import { useEffect, useMemo, useRef } from "react";
import { MapContainer, TileLayer, Marker, Polyline, useMap, useMapEvents } from "react-leaflet";
import L from "leaflet";
import type { LatLngExpression } from "leaflet";

const OSM = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";

const guessIcon = L.divIcon({
  className: "pin-wrap",
  html: '<div class="pin pin--guess"><div class="pin__dot"></div></div>',
  iconSize: [32, 42],
  iconAnchor: [16, 42],
});

const truthIcon = L.divIcon({
  className: "pin-wrap",
  html: '<div class="pin pin--truth"><div class="pin__dot"></div></div>',
  iconSize: [32, 42],
  iconAnchor: [16, 42],
});

const opponentIcon = L.divIcon({
  className: "pin-wrap",
  html: '<div class="pin pin--opponent"><div class="pin__dot"></div></div>',
  iconSize: [32, 42],
  iconAnchor: [16, 42],
});

export function normalizeLon(lon: number): number {
  return ((((lon + 180) % 360) + 360) % 360) - 180;
}

export function clampLat(lat: number): number {
  return Math.max(-85, Math.min(85, lat));
}

function MapClickHandler({ onPick }: { onPick: (lat: number, lon: number) => void }) {
  useMapEvents({
    click(e) {
      onPick(clampLat(e.latlng.lat), normalizeLon(e.latlng.lng));
    },
  });
  return null;
}

function MapBounds({ points }: { points: LatLngExpression[] }) {
  const map = useMap();
  useEffect(() => {
    if (points.length < 2) return;
    const bounds = L.latLngBounds(points);
    map.fitBounds(bounds, { padding: [60, 60], maxZoom: 12 });
  }, [map, points]);
  return null;
}

function ZoomLimits({ min, max }: { min: number; max: number }) {
  const map = useMap();
  useEffect(() => {
    map.setMinZoom(min);
    map.setMaxZoom(max);
  }, [map, min, max]);
  return null;
}

/** Keep map tiles filling container after expand/resize. */
function MapResizeFix({ active }: { active: boolean }) {
  const map = useMap();

  useEffect(() => {
    const invalidate = () => {
      map.invalidateSize({ animate: false, pan: false });
    };

    const runBurst = () => {
      invalidate();
      const delays = [50, 120, 300, 500];
      const timers = delays.map((ms) => window.setTimeout(invalidate, ms));
      return () => timers.forEach(clearTimeout);
    };

    let cancelBurst = runBurst();
    const widget = map.getContainer().closest(".map-widget") as HTMLElement | null;
    const observeTarget = widget ?? map.getContainer().parentElement;
    if (!observeTarget) return () => cancelBurst();

    const ro = new ResizeObserver(() => {
      requestAnimationFrame(invalidate);
    });
    ro.observe(observeTarget);

    return () => {
      cancelBurst();
      ro.disconnect();
    };
  }, [map, active]);

  return null;
}

function MapZoomButtons() {
  const map = useMap();
  return (
    <div className="map-zoom-btns">
      <button type="button" aria-label="Zoom in" onClick={() => map.zoomIn()}>
        +
      </button>
      <button type="button" aria-label="Zoom out" onClick={() => map.zoomOut()}>
        −
      </button>
    </div>
  );
}

/** Geodesic-ish line that handles dateline crossing visually. */
function ResultLine({ guess, truth }: { guess: { lat: number; lon: number }; truth: { lat: number; lon: number } }) {
  const positions = useMemo(() => buildGeodesicLine(guess, truth, 64), [guess, truth]);
  return <Polyline positions={positions} pathOptions={{ color: "#ffc107", weight: 4, opacity: 0.9 }} />;
}

function buildGeodesicLine(
  a: { lat: number; lon: number },
  b: { lat: number; lon: number },
  steps: number
): LatLngExpression[] {
  const pts: LatLngExpression[] = [];
  let lon1 = a.lon;
  let lon2 = b.lon;
  const dLon = lon2 - lon1;
  if (Math.abs(dLon) > 180) {
    if (dLon > 0) lon1 += 360;
    else lon2 += 360;
  }
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const lat = a.lat + (b.lat - a.lat) * t;
    const lon = lon1 + (lon2 - lon1) * t;
    pts.push([lat, normalizeLon(lon)]);
  }
  return pts;
}

interface Props {
  guess: { lat: number; lon: number } | null;
  truth?: { lat: number; lon: number } | null;
  opponentGuess?: { lat: number; lon: number } | null;
  onGuess?: (lat: number, lon: number) => void;
  startZoom?: number;
  maxZoom?: number;
  minZoom?: number;
  center?: [number, number];
  expanded?: boolean;
  mapKey?: string;
  className?: string;
}

export function GameMap({
  guess,
  truth,
  opponentGuess,
  onGuess,
  startZoom = 2,
  maxZoom = 15,
  minZoom = 1,
  center = [20, 0],
  expanded = false,
  mapKey = "map",
  className = "",
}: Props) {
  const initialCenter = useRef(center);
  const isResult = !!(guess && truth);

  const resultCenter = useMemo<[number, number] | null>(() => {
    if (!guess || !truth) return null;
    return [(guess.lat + truth.lat) / 2, normalizeLon((guess.lon + truth.lon) / 2)];
  }, [guess, truth]);

  return (
    <div className={`game-map ${expanded ? "game-map--expanded" : ""} ${className}`}>
      <MapContainer
        key={mapKey}
        center={isResult && resultCenter ? resultCenter : initialCenter.current}
        zoom={isResult ? 3 : startZoom}
        className="game-map__leaflet"
        zoomControl={false}
        attributionControl
        worldCopyJump
        maxBounds={[
          [-85, -180],
          [85, 180],
        ]}
        maxBoundsViscosity={0.8}
        scrollWheelZoom
        dragging
        doubleClickZoom
        touchZoom
        boxZoom={expanded}
      >
        <TileLayer
          url={OSM}
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
          noWrap={false}
        />
        <ZoomLimits min={minZoom} max={maxZoom} />
        <MapResizeFix active={expanded} />
        <MapZoomButtons />
        {onGuess && <MapClickHandler onPick={onGuess} />}
        {guess && <Marker position={[guess.lat, normalizeLon(guess.lon)]} icon={guessIcon} />}
        {opponentGuess && (
          <Marker position={[opponentGuess.lat, normalizeLon(opponentGuess.lon)]} icon={opponentIcon} />
        )}
        {truth && <Marker position={[truth.lat, normalizeLon(truth.lon)]} icon={truthIcon} />}
        {guess && truth && (
          <>
            <ResultLine guess={guess} truth={truth} />
            <MapBounds
              points={[
                [guess.lat, guess.lon],
                [truth.lat, truth.lon],
              ]}
            />
          </>
        )}
      </MapContainer>
    </div>
  );
}
