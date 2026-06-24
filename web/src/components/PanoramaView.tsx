import { useEffect, useRef, useState, useCallback } from "react";
import { Viewer } from "@photo-sphere-viewer/core";
import "@photo-sphere-viewer/core/index.css";

interface Props {
  src: string;
  heading?: number;
  pitch?: number;
  zoom?: number;
  allowLook?: boolean;
  allowZoom?: boolean;
  onMovement?: (units: number) => void;
  onReady?: () => void;
  onError?: () => void;
}

const SPHERE_RATIO = 1.92; // only true ~360° equirectangular (2:1)
const LOAD_TIMEOUT_MS = 12000;

export function PanoramaView({
  src,
  heading = 0,
  pitch = 0,
  zoom = 50,
  allowLook = true,
  allowZoom = true,
  onMovement,
  onReady,
  onError,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<Viewer | null>(null);
  const readyRef = useRef(false);
  const onReadyRef = useRef(onReady);
  const onErrorRef = useRef(onError);
  const onMovementRef = useRef(onMovement);

  onReadyRef.current = onReady;
  onErrorRef.current = onError;
  onMovementRef.current = onMovement;

  const [mode, setMode] = useState<"loading" | "sphere" | "flat" | "error">("loading");
  const [flatState, setFlatState] = useState({ x: 0, y: 0, scale: 1.25, dragging: false });
  const [flatLoaded, setFlatLoaded] = useState(false);
  const dragStart = useRef({ x: 0, y: 0, ox: 0, oy: 0 });
  const movement = useRef(0);

  const signalReady = useCallback(() => {
    if (readyRef.current) return;
    readyRef.current = true;
    onReadyRef.current?.();
  }, []);

  const signalError = useCallback(() => {
    if (readyRef.current) return;
    onErrorRef.current?.();
    setMode("error");
  }, []);

  // Detect image type + timeout fallback
  useEffect(() => {
    readyRef.current = false;
    setMode("loading");
    setFlatLoaded(false);
    setFlatState({ x: 0, y: 0, scale: 1.25, dragging: false });

    let cancelled = false;
    const timeout = window.setTimeout(() => {
      if (!cancelled && !readyRef.current) {
        // Stuck — try flat mode anyway
        setMode((m) => (m === "loading" ? "flat" : m));
      }
    }, LOAD_TIMEOUT_MS);

    const img = new Image();
    img.onload = () => {
      if (cancelled) return;
      window.clearTimeout(timeout);
      const isSphere = img.naturalWidth >= img.naturalHeight * SPHERE_RATIO;
      setMode(isSphere ? "sphere" : "flat");
    };
    img.onerror = () => {
      if (!cancelled) {
        window.clearTimeout(timeout);
        signalError();
      }
    };
    img.src = src;

    return () => {
      cancelled = true;
      window.clearTimeout(timeout);
    };
  }, [src, signalError]);

  // Photo Sphere Viewer (only for real 360° photos)
  useEffect(() => {
    if (mode !== "sphere" || !containerRef.current) return;

    let destroyed = false;
    const readyTimeout = window.setTimeout(() => {
      if (!destroyed && !readyRef.current) setMode("flat");
    }, LOAD_TIMEOUT_MS);

    const viewer = new Viewer({
      container: containerRef.current,
      panorama: src,
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
      if (!destroyed) setMode("flat");
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
  }, [mode, src, heading, pitch, zoom, allowLook, allowZoom, signalReady]);

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

  if (mode === "error") {
    return (
      <div className="panorama panorama--error">
        <p>📷</p>
        <p>Фото не найдено</p>
        <small>python3 scripts/download_assets.py</small>
      </div>
    );
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
        src={src}
        alt=""
        draggable={false}
        onLoad={() => {
          setFlatLoaded(true);
          signalReady();
        }}
        onError={() => signalError()}
        style={{
          transform: `translate(${flatState.x}px, ${flatState.y}px) scale(${flatState.scale})`,
          opacity: flatLoaded ? 1 : 0,
        }}
      />
      {!flatLoaded && (
        <div className="panorama__loader panorama__loader--flat" />
      )}
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
