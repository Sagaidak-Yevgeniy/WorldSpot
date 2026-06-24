import { useEffect, useMemo } from "react";
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

function MapClickHandler({ onPick }: { onPick: (lat: number, lon: number) => void }) {
  useMapEvents({
    click(e) {
      onPick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

function MapBounds({ points }: { points: LatLngExpression[] }) {
  const map = useMap();
  useEffect(() => {
    if (points.length < 2) return;
    map.fitBounds(L.latLngBounds(points), { padding: [60, 60], maxZoom: 12 });
  }, [map, points]);
  return null;
}

function ZoomClamp({ min, max }: { min: number; max: number }) {
  const map = useMap();
  useEffect(() => {
    map.setMinZoom(min);
    map.setMaxZoom(max);
  }, [map, min, max]);
  return null;
}

interface Props {
  guess: { lat: number; lon: number } | null;
  truth?: { lat: number; lon: number } | null;
  onGuess?: (lat: number, lon: number) => void;
  startZoom?: number;
  maxZoom?: number;
  center?: [number, number];
  expanded?: boolean;
  className?: string;
}

export function GameMap({
  guess,
  truth,
  onGuess,
  startZoom = 2,
  maxZoom = 15,
  center = [20, 0],
  expanded = false,
  className = "",
}: Props) {
  const mapCenter = useMemo<[number, number]>(() => {
    if (guess && truth) {
      return [(guess.lat + truth.lat) / 2, (guess.lon + truth.lon) / 2];
    }
    if (guess) return [guess.lat, guess.lon];
    return center;
  }, [guess, truth, center]);

  const zoom = guess && truth ? undefined : startZoom;
  const line: LatLngExpression[] =
    guess && truth
      ? [
          [guess.lat, guess.lon],
          [truth.lat, truth.lon],
        ]
      : [];

  return (
    <div className={`game-map ${expanded ? "game-map--expanded" : ""} ${className}`}>
      <MapContainer
        center={mapCenter}
        zoom={zoom ?? 3}
        className="game-map__leaflet"
        zoomControl={expanded}
        attributionControl
        scrollWheelZoom={expanded}
        dragging
        doubleClickZoom={expanded}
      >
        <TileLayer url={OSM} attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>' />
        <ZoomClamp min={1} max={maxZoom} />
        {onGuess && <MapClickHandler onPick={onGuess} />}
        {guess && <Marker position={[guess.lat, guess.lon]} icon={guessIcon} />}
        {truth && <Marker position={[truth.lat, truth.lon]} icon={truthIcon} />}
        {line.length === 2 && (
          <>
            <Polyline positions={line} pathOptions={{ color: "#ffc107", weight: 4, opacity: 0.9 }} />
            <MapBounds points={line} />
          </>
        )}
      </MapContainer>
    </div>
  );
}
