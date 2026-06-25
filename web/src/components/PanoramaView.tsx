import { useCallback, useEffect, useRef, useState } from "react";
import { assetUrl } from "../lib/assets";

interface Props {
  sources: string[];
  heading?: number;
  pitch?: number;
  zoom?: number;
  allowLook?: boolean;
  allowZoom?: boolean;
  onMovement?: (units: number) => void;
  onReady?: () => void;
}

const SOURCE_TIMEOUT_MS = 7000;

export function PanoramaView({
  sources,
  allowLook = true,
  allowZoom = true,
  onMovement,
  onReady,
}: Props) {
  const urls = sources.length ? sources : [assetUrl("panoramas/oslo.jpg"), assetUrl("panorama/oslo_01?n=0")];
  const [index, setIndex] = useState(0);
  const [loaded, setLoaded] = useState(false);
  const [failed, setFailed] = useState(false);
  const readyRef = useRef(false);
  const onReadyRef = useRef(onReady);
  const onMovementRef = useRef(onMovement);
  const dragStart = useRef({ x: 0, y: 0, ox: 0, oy: 0 });
  const movement = useRef(0);
  const [view, setView] = useState({ x: 0, y: 0, scale: 1.2, dragging: false });

  onReadyRef.current = onReady;
  onMovementRef.current = onMovement;

  const activeSrc = urls[index] ?? urls[0];

  const signalReady = useCallback(() => {
    if (readyRef.current) return;
    readyRef.current = true;
    onReadyRef.current?.();
  }, []);

  const tryNext = useCallback(() => {
    setIndex((i) => {
      if (i >= urls.length - 1) {
        setFailed(true);
        signalReady();
        return i;
      }
      setLoaded(false);
      return i + 1;
    });
  }, [urls.length, signalReady]);

  useEffect(() => {
    readyRef.current = false;
    setIndex(0);
    setLoaded(false);
    setFailed(false);
    setView({ x: 0, y: 0, scale: 1.2, dragging: false });
  }, [urls.join("|")]);

  useEffect(() => {
    if (loaded || failed) return;
    const t = window.setTimeout(() => tryNext(), SOURCE_TIMEOUT_MS);
    return () => window.clearTimeout(t);
  }, [activeSrc, loaded, failed, tryNext]);

  const onLoad = () => {
    setLoaded(true);
    signalReady();
  };

  const onError = () => tryNext();

  const onDown = (e: React.MouseEvent) => {
    if (!allowLook) return;
    e.preventDefault();
    setView((s) => ({ ...s, dragging: true }));
    dragStart.current = { x: e.clientX, y: e.clientY, ox: view.x, oy: view.y };
  };

  const onMove = (e: React.MouseEvent) => {
    if (!view.dragging || !allowLook) return;
    const dx = e.clientX - dragStart.current.x;
    const dy = e.clientY - dragStart.current.y;
    movement.current += Math.abs(dx) + Math.abs(dy);
    onMovementRef.current?.(movement.current);
    setView((s) => ({
      ...s,
      x: dragStart.current.ox + dx,
      y: dragStart.current.oy + dy,
    }));
  };

  const onUp = () => setView((s) => ({ ...s, dragging: false }));

  const zoom = (delta: number) => {
    if (!allowZoom) return;
    setView((s) => ({
      ...s,
      scale: Math.min(3.5, Math.max(1, s.scale + delta * 0.15)),
    }));
  };

  if (failed) {
    return <div className="panorama panorama--fallback" />;
  }

  return (
    <div
      className={`panorama panorama--flat ${view.dragging ? "panorama--grabbing" : ""}`}
      onMouseDown={onDown}
      onMouseMove={onMove}
      onMouseUp={onUp}
      onMouseLeave={onUp}
      onWheel={(e) => {
        e.preventDefault();
        zoom(e.deltaY > 0 ? -1 : 1);
      }}
    >
      {!loaded && (
        <div className="panorama panorama--loading">
          <div className="panorama__loader" />
        </div>
      )}
      <img
        key={activeSrc}
        src={activeSrc}
        alt=""
        draggable={false}
        className="panorama__img"
        onLoad={onLoad}
        onError={onError}
        style={{
          transform: `translate(${view.x}px, ${view.y}px) scale(${view.scale})`,
          visibility: loaded ? "visible" : "hidden",
        }}
      />
      {allowZoom && loaded && (
        <div className="panorama__zoom">
          <button type="button" onClick={() => zoom(1)} aria-label="+">
            +
          </button>
          <button type="button" onClick={() => zoom(-1)} aria-label="−">
            −
          </button>
        </div>
      )}
      {view.dragging && <div className="panorama__crosshair" />}
    </div>
  );
}
