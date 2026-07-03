import { Easing, interpolate, interpolateColors } from "remotion";
import T from "./motion.tokens.json";

// TOKENS DE MOTION — única fuente de timing/curvas/paleta del mundo de la página.
// Ningún master escribe un bezier o una duración literal: todo pasa por aquí.

export const TOK = T;
export const PAL = T.palette;

type CurveName = keyof typeof T.curve;
const bez = (name: CurveName) => {
  const [a, b, c, d] = T.curve[name].$value as [number, number, number, number];
  return Easing.bezier(a, b, c, d);
};

export const CURVE = {
  enter: bez("enter"),
  exit: bez("exit"),
  standard: bez("standard"),
  mass: bez("mass"),
  countLand: bez("countLand"),
};

// progreso 0..1 con curva de token entre dos frames
export const tprog = (
  frame: number,
  from: number,
  to: number,
  curve: keyof typeof CURVE = "enter",
) =>
  interpolate(frame, [from, to], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: CURVE[curve],
  });

// hold de lectura: max(piso, chars/17cps) en frames (Netflix es-MX)
export const holdF = (chars: number) =>
  Math.max(T.hold.numberMinF, Math.ceil((chars / T.hold.charsPerSec) * T.fps));

// progreso LINEAL (para ramps de COLOR: el destello vive en tiempo real,
// sin easing — la curva es del movimiento, no de la tinta)
export const lprog = (frame: number, from: number, to: number) =>
  interpolate(frame, [from, to], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

// FIRMA: el acento vive en la transición — color gris→esmeralda→hueso dentro
// de la ventana de entrada (primer flashWindowPct del tiempo), reposa en hueso.
// t = progreso 0..1 de la ENTRADA del elemento. restColor = color de reposo.
// Interpolación suave (no switch): pasa POR el esmeralda y decae al reposo.
export const inkFlash = (t: number, restColor: string = PAL.ink) => {
  const w = T.accent.flashWindowPct;
  return interpolateColors(
    Math.min(Math.max(t, 0), 1),
    [0, w * 0.45, w, 1],
    [PAL.faint, PAL.accent, restColor, restColor],
  );
};
