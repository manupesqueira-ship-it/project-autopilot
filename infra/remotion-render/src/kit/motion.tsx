import React from "react";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

// MOTION TOKENS — curvas nombradas + springs + stagger + odómetro.
// Regla (auditoría 2026-07-03): CERO interpolate sin easing, CERO spring sin config.

export const EASE = {
  enter: Easing.bezier(0.05, 0.7, 0.1, 1),     // MD3 emphasized-decelerate: entradas
  exit: Easing.bezier(0.3, 0, 0.8, 0.15),      // MD3 emphasized-accelerate: salidas
  update: Easing.bezier(0.4, 0, 0.2, 1),       // cambios de estado
  dramatic: Easing.bezier(0.62, 0, 0.18, 1),   // reveals de clímax (acelera y frena tarde)
};

export const SPR = {
  SMOOTH: { damping: 200 },                          // default: sin rebote caricatura
  SNAPPY: { damping: 22, stiffness: 300, mass: 0.8 },// pops de énfasis
  HERO: { damping: 14, stiffness: 120, mass: 0.9 },  // 1 uso por reel (clímax)
};

// stagger en frames (GSAP-style): 60-100ms = 2-3 frames a 30fps
export const stag = (i: number, each = 2.5) => Math.round(i * each);

// progreso eased tipado (reemplaza interpolate crudo en beats)
export const prog = (frame: number, from: number, to: number, ease: (t: number) => number = EASE.enter) =>
  interpolate(frame, [from, to], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });

// duración efectiva del beat (dentro de NewsReel viene por prop; suelto usa la comp)
export const useBeatDur = (durF?: number) => {
  const { durationInFrames } = useVideoConfig();
  return durF ?? durationInFrames;
};

// ── ODÓMETRO por dígito ─────────────────────────────────────────────────────
// Cifras héroe premium: cada dígito RUEDA en su columna (el de la derecha gira más
// vueltas), tabular, sin jitter horizontal. land = frame donde aterriza.
export const Odometer: React.FC<{
  value: string;            // string final ya formateado (ej. "$32,234" o "3.5")
  fontSize: number;
  color: string;
  start?: number;
  land: number;
  weight?: number;
  glow?: string;            // color del glow al aterrizar (opcional)
  glowAt?: number;          // frame desde el que aplica el glow
}> = ({ value, fontSize, color, start = 6, land, weight = 800, glow, glowAt }) => {
  const frame = useCurrentFrame();
  const t = prog(frame, start, land, EASE.dramatic);
  const H = Math.round(fontSize * 1.06);
  const digitsFromRight = (() => {
    let n = 0;
    const arr: number[] = [];
    for (let i = value.length - 1; i >= 0; i--) {
      if (/\d/.test(value[i])) { arr[i] = n; n++; } else arr[i] = -1;
    }
    return arr;
  })();
  const glowOn = glow && frame >= (glowAt ?? land);
  const filter = glowOn
    ? `drop-shadow(0 0 4px ${glow}AA) drop-shadow(0 0 14px ${glow}66) drop-shadow(0 0 42px ${glow}40) drop-shadow(0 0 110px ${glow}26)`
    : "none";
  return (
    <div style={{ display: "flex", alignItems: "flex-start", filter, fontVariantNumeric: "tabular-nums" }}>
      {value.split("").map((ch, i) => {
        if (!/\d/.test(ch)) {
          return (
            <span key={i} style={{ fontSize, fontWeight: weight, color, lineHeight: `${H}px`, letterSpacing: "-0.02em" }}>{ch === " " ? " " : ch}</span>
          );
        }
        const d = parseInt(ch, 10);
        const cycles = Math.min(3, 1 + digitsFromRight[i]);      // derecha gira más
        const pos = t * (cycles * 10 + d);                        // termina exacto en d
        const off = (pos % 10) * H;
        return (
          <span key={i} style={{ display: "inline-block", height: H, overflow: "hidden", verticalAlign: "top" }}>
            <span style={{ display: "block", transform: `translateY(${-off}px)` }}>
              {Array.from({ length: 11 }).map((_, k) => (
                <span key={k} style={{ display: "block", fontSize, fontWeight: weight, color, lineHeight: `${H}px`, letterSpacing: "-0.02em", textAlign: "center" }}>
                  {k % 10}
                </span>
              ))}
            </span>
          </span>
        );
      })}
    </div>
  );
};
