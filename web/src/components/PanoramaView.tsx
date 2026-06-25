import { useEffect, useRef, useState, useCallback } from "react";
import { Viewer } from "@photo-sphere-viewer/core";
import "@photo-sphere-viewer/core/index.css";

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

const SPHERE_RATIO = 1.92;
const SOURCE_TIMEOUT_MS = 8000;
const TOTAL_TIMEOUT_MS = 25000;

export function PanoramaView({
  sources,
  heading = 0,
  pitch = 0,
  zoom = 50,
  allowLook = true,
  allowZoom = true,
  onMovement,
  onReady,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<Viewer | null>(null);
  const readyRef = useRef(false);
  const onReadyRef = useRef(onReady);
  const onMovementRef = useRef(onMovement);

  onReadyRef.current = onReady;
  onMovementRef.current = onMovement;

  const urls = sources.length ? sources : ["/panoramas/oslo.jpg", "/panorama/oslo_01?n=0"];
  const [sourceIndex, setSourceIndex] = useState(0);
  const sourceIndexRef = useRef(0);
  sourceIndexRef.current = sourceIndex;
  const activeSrc = urls[sourceIndex] ?? urls[0];
  const [mode, setMode] = useState<"loading" | "sphere" | "flat" | "failed">("loading");
  const [flatState, setFlatState] = useState({ x: 0, y: 0, scale: 1.25, dragging: false });
  const [flatLoaded, setFlatLoaded] = useState(false);
  const dragStart = useRef({ x: 0, y: 0, ox: 0, oy: 0 });
  const movement = useRef(0);

  const signalReady = useCallback(() => {
    if (readyRef.current) return;
    readyRef.current = true;
    onReadyRef.current?.();
  }, []);

  const failAll = useCallback(() => {
    setMode("failed");
    signalReady();
  }, [signalReady]);

  const tryNextSource = useCallback(() => {
    if (sourceIndexRef.current >= urls.length - 1) {
      failAll();
      return false;
    }
    readyRef.current = false;
    setFlatLoaded(false);
    setMode("loading");
    setSourceIndex((i) => i + 1);
    return true;
  }, [urls.length, failAll]);

  useEffect(() => {
    readyRef.current = false;
    setSourceIndex(0);
    setMode("loading");
    setFlatLoaded(false);
    setFlatState({ x: 0, y: 0, scale: 1.25, dragging: false });
  }, [urls.join("|")]);

  useEffect(() => {
    const hardStop = window.setTimeout(() => {
      if (!readyRef.current) failAll();
    }, TOTAL_TIMEOUT_MS);
    return () => window.clearTimeout(hardStop);
  }, [urls.join("|"), failAll]);

  useEffect(() => {
    if (mode === "failed") return;

    let cancelled = false;
    const timeout = window.setTimeout(() => {
      if (!cancelled && !readyRef.current) tryNextSource();
    }, SOURCE_TIMEOUT_MS);

    const img = new Image();
    img.onload = () => {
      if (cancelled) return;
      window.clearTimeout(timeout);
      if (img.naturalWidth < 400 || img.naturalHeight < 200) {
        tryNextSource();
        return;
      }
      const isSphere = img.naturalWidth >= img.naturalHeight * SPHERE_RATIO;
      setMode(isSphere ? "sphere" : "flat");
    };
    img.onerror = () => {
      if (cancelled) return;
      window.clearTimeout(timeout);
      tryNextSource();
    };
    img.src = activeSrc;

    return () => {
      cancelled = true;
      window.clearTimeout(timeout);
    };
  }, [activeSrc, tryNextSource, mode]);

  useEffect(() => {
    if (mode !== "sphere" || !containerRef.current) return;

    let destroyed = false;
    const readyTimeout = window.setTimeout(() => {
      if (!destroyed && !readyRef.current) tryNextSource();
    }, SOURCE_TIMEOUT_MS);

    const viewer = new Viewer({
      container: containerRef.current,
      panorama: activeSrc,
      defaultYaw: `${heading}deg`,
      defaultPitch: `${pitch}deg`,
      defaultZoomLvl: Math.min(100, Math.max(0, zoom)),
      navbar: false,
      mousemove: allowLook,
      mousewheel: allowZoom,
      touchmoveTwoFingers: allowLook,
    });

    viewerRef.current = viewer;

    const onReadyEvt = () => {
      window.clearTimeout(readyTimeout);
      signalReady();
    };
    const onErrorEvt = () => {
      window.clearTimeout(readyTimeout);
      if (!destroyed) tryNextSource();
    };

    viewer.addEventListener("ready", onReadyEvt);
    viewer.addEventListener("panorama-error" as never, onErrorEvt);
    viewer.addEventListener("position-updated", () => {
      movement.current += 0.5;
      onMovementRef.current?.(movement.current);
    });

    return () => {
      destroyed = true;
      window.clearTimeout(readyTimeout);
      viewer.destroy();
      viewerRef.current = null;
    };
  }, [mode, activeSrc, heading, pitch, zoom, allowLook, allowZoom, signalReady, tryNextSource]);

  const onFlatDown = useCallback(
    (e: React.MouseEvent) => {
      if (!allowLook) return;
      e.preventDefault();
      setFlatState((s) => ({ ...s, dragging: true }));
      dragStart.current = { x: e.clientX, y: e.clientY, ox: flatState.x, oy: flatState.y };
    },
    [allowLook, flatState.x, flatState.y]
  );

  const onFlatMove = useCallback(
    (e: React.MouseEvent) => {
      if (!flatState.dragging || !allowLook) return;
      const dx = e.clientX - dragStart.current.x;
      const dy = e.clientY - dragStart.current.y;
      movement.current += Math.abs(dx) + Math.abs(dy);
      onMovementRef.current?.(movement.current);
      setFlatState((s) => ({
        ...s,
        x: dragStart.current.ox + dx,
        y: dragStart.current.oy + dy,
      }));
    },
    [flatState.dragging, allowLook]
  );

  const onFlatUp = useCallback(() => {
    setFlatState((s) => ({ ...s, dragging: false }));
  }, []);

  const zoomFlat = (delta: number) => {
    if (!allowZoom) return;
    setFlatState((s) => ({
      ...s,
      scale: Math.min(3.5, Math.max(1, s.scale + delta * 0.15)),
    }));
  };

  if (mode === "loading") {
    return (
      <div className="panorama panorama--loading">
        <div className="panorama__loader" />
      </div>
    );
  }

  if (mode === "failed") {
    return <div className="panorama panorama--fallback" />;
  }

  if (mode === "sphere") {
    return (
      <div className="panorama">
        <div ref={containerRef} className="panorama__sphere" />
        {allowZoom && (
          <div className="panorama__zoom">
            <button
              type="button"
              onClick={() => viewerRef.current?.zoom(viewerRef.current.getZoomLevel() + 5)}
              aria-label="+"
            >
              +
            </button>
            <button
              type="button"
              onClick={() => viewerRef.current?.zoom(viewerRef.current.getZoomLevel() - 5)}
              aria-label="−"
            >
              −
            </button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div
      className={`panorama panorama--flat ${flatState.dragging ? "panorama--grabbing" : ""}`}
      onMouseDown={onFlatDown}
      onMouseMove={onFlatMove}
      onMouseUp={onFlatUp}
      onMouseLeave={onFlatUp}
      onWheel={(e) => {
        e.preventDefault();
        zoomFlat(e.deltaY > 0 ? -1 : 1);
      }}
    >
      <img
        key={activeSrc}
        src={activeSrc}
        alt=""
        draggable={false}
        onLoad={() => {
          setFlatLoaded(true);
          signalReady();
        }}
        onError={() => tryNextSource()}
        style={{
          transform: `translate(${flatState.x}px, ${flatState.y}px) scale(${flatState.scale})`,
          opacity: flatLoaded ? 1 : 0,
        }}
      />
      {!flatLoaded && <div className="panorama__loader panorama__loader--flat" />}
      {allowZoom && (
        <div className="panorama__zoom">
          <button type="button" onClick={() => zoomFlat(1)}>
            +
          </button>
          <button type="button" onClick={() => zoomFlat(-1)}>
            −
          </button>
        </div>
      )}
      {flatState.dragging && <div className="panorama__crosshair" />}
    </div>
  );
}
