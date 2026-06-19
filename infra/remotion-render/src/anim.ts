import { interpolate, spring } from "remotion";
import type { CSSProperties } from "react";

// Curvas de entrada compartidas — Style Bible §5.4:
//   "Easing overshoot, nunca lineal: anticipation + overshoot + settle
//    (spring rebote SUTIL), stagger 2-4 frames. No el bouncy del v11."
//
// UNA fuente de verdad para las entradas de TODOS los beats (Track A: lo hereda
// CADA beat). Antes cada beat hand-rolleaba su propio spring (damping 11-18,
// mass 0.6-0.9) -> overshoot inconsistente, imposible de afinar en bloque. Aquí
// el overshoot queda LOCKED y se tunea desde un solo lugar.
//
// El overshoot lo da el SPRING sobre la posición/escala (rebasa el destino y
// asienta). La opacidad NO usa spring (no tiene sentido rebasar 1): es un fade
// lineal-clamp corto. Así el "pop" se ve en el MOVIMIENTO, no en un parpadeo.

type Spring = {
  damping?: number;
  mass?: number;
  stiffness?: number;
  overshootClamping?: boolean;
};

// Configs LOCKED. Sub-amortiguado (ζ<1) = overshoot. Elegidos para overshoot
// SUTIL premium, NO el bouncy del v11 (RECHAZADO). Aproximación de ζ con
// stiffness/mass de abajo: entrance ζ≈0.65 (~7%), soft ζ≈0.73 (~5%).
export const SPRING: Record<"entrance" | "soft" | "settle", Spring> = {
  // entrada principal (hero / stat / número): pop con overshoot sutil ~7%
  entrance: { damping: 13, mass: 0.85, stiffness: 120 },
  // elementos secundarios (caption, chips, reglas): overshoot mínimo ~5%
  soft: { damping: 16, mass: 0.7, stiffness: 110 },
  // cosas que NO deben rebotar (count-up settle, barras de dato): sin overshoot
  settle: { damping: 200, mass: 1, stiffness: 120 },
};

// Stagger por defecto entre elementos hermanos (§5.4: 2-4 frames).
export const STAGGER = 3;

// delay en frames del i-ésimo elemento de una serie escalonada.
export const stagger = (index: number, perItem = STAGGER, base = 0) =>
  base + index * perItem;

// progreso 0..1 con overshoot (rebasa 1 y asienta). delay en frames.
export const enterProgress = (
  frame: number,
  fps: number,
  delay = 0,
  config: Spring = SPRING.entrance,
) => spring({ frame: frame - delay, fps, config });

const clampFade = (frame: number, delay: number, fadeFrames: number) =>
  interpolate(frame, [delay, delay + fadeFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

export type EnterOpts = {
  frame: number;
  fps: number;
  delay?: number;
  fadeFrames?: number;
  config?: Spring;
};

// Entrada "rise": sube desde `distance`px abajo con overshoot + fade.
// Reemplaza el `rise()` inline duplicado en los beats.
export const riseIn = ({
  frame,
  fps,
  delay = 0,
  fadeFrames = 6,
  config = SPRING.entrance,
  distance = 18,
}: EnterOpts & { distance?: number }): CSSProperties => {
  const s = enterProgress(frame, fps, delay, config);
  return {
    opacity: clampFade(frame, delay, fadeFrames),
    transform: `translateY(${(1 - s) * distance}px)`,
  };
};

// Entrada "pop": escala desde `from` (<1) hasta 1 con overshoot + fade.
export const popIn = ({
  frame,
  fps,
  delay = 0,
  fadeFrames = 6,
  config = SPRING.entrance,
  from = 0.85,
}: EnterOpts & { from?: number }): CSSProperties => {
  const s = enterProgress(frame, fps, delay, config);
  return {
    opacity: clampFade(frame, delay, fadeFrames),
    transform: `scale(${from + (1 - from) * s})`,
  };
};

// Entrada hero: combina rise + pop (sube y escala con overshoot). Para el dato
// enorme / objeto protagonista de un beat.
export const riseScaleIn = ({
  frame,
  fps,
  delay = 0,
  fadeFrames = 6,
  config = SPRING.entrance,
  distance = 30,
  from = 0.7,
}: EnterOpts & { distance?: number; from?: number }): CSSProperties => {
  const s = enterProgress(frame, fps, delay, config);
  return {
    opacity: clampFade(frame, delay, fadeFrames),
    transform: `translateY(${(1 - s) * distance}px) scale(${from + (1 - from) * s})`,
  };
};
