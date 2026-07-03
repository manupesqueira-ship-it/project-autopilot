import type { TransitionPresentation, TransitionPresentationComponentProps } from "@remotion/transitions";
import React from "react";
import { AbsoluteFill } from "remotion";

// GRAMÁTICA DE EDICIÓN en-render (auditoría 2026-07-03 #6). Presentations custom para
// TransitionSeries: el reel es UNA pieza con cámara continua, no MP4s pegados con dip.
// zoomThrough = profundizar/revelar (cambio de escala de dato) · whip = traslado de
// sujeto · dipToBlack = separador de capítulo (ÚNICO uso). Hard cut = default (sin transición).

const Zoom: React.FC<TransitionPresentationComponentProps<Record<string, never>>> = ({
  children, presentationDirection, presentationProgress,
}) => {
  const p = presentationProgress;
  const exiting = presentationDirection === "exiting";
  const scale = exiting ? 1 + 0.55 * p : 0.72 + 0.28 * p;
  const blur = exiting ? 16 * p : 12 * (1 - p);
  const opacity = exiting ? 1 - Math.pow(p, 1.6) : Math.min(1, p * 1.8);
  return (
    <AbsoluteFill style={{ transform: `scale(${scale})`, filter: `blur(${blur}px)`, opacity, transformOrigin: "50% 46%" }}>
      {children}
    </AbsoluteFill>
  );
};
export const zoomThrough = (): TransitionPresentation<Record<string, never>> => ({ component: Zoom, props: {} });

const Whip: React.FC<TransitionPresentationComponentProps<{ dir: 1 | -1 }>> = ({
  children, presentationDirection, presentationProgress, passedProps,
}) => {
  const p = presentationProgress;
  const d = passedProps.dir ?? 1;
  const exiting = presentationDirection === "exiting";
  const x = exiting ? -d * 1080 * p : d * 1080 * (1 - p);
  const blur = 26 * Math.sin(Math.PI * p); // pico de blur en el centro del corte
  return (
    <AbsoluteFill style={{ transform: `translateX(${x}px)`, filter: `blur(${blur * 0.4}px) drop-shadow(0 0 0 transparent)`, opacity: 1 }}>
      <AbsoluteFill style={{ filter: `blur(${blur}px)`, transform: `scaleX(${1 + blur * 0.004})` }}>{children}</AbsoluteFill>
    </AbsoluteFill>
  );
};
export const whipPan = (dir: 1 | -1 = 1): TransitionPresentation<{ dir: 1 | -1 }> => ({ component: Whip, props: { dir } });

const Dip: React.FC<TransitionPresentationComponentProps<Record<string, never>>> = ({
  children, presentationDirection, presentationProgress,
}) => {
  const p = presentationProgress;
  const exiting = presentationDirection === "exiting";
  const opacity = exiting ? 1 - Math.min(1, p * 2) : Math.max(0, p * 2 - 1);
  return (
    <AbsoluteFill style={{ backgroundColor: "#050505" }}>
      <AbsoluteFill style={{ opacity }}>{children}</AbsoluteFill>
    </AbsoluteFill>
  );
};
export const dipToBlack = (): TransitionPresentation<Record<string, never>> => ({ component: Dip, props: {} });
